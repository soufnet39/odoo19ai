/** @odoo-module **/
import { reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";

let lineIdCounter = 1;

export const posService = {
    dependencies: ["orm"],
    start(env, { orm }) {
        const service = reactive({
            session: null,
            config: null,
            user: null,
            company: null,
            products: [],
            categories: [],
            partners: [],
            paymentModes: [],
            recentOrders: [],

            // Multi-orders state
            orders: [],
            selectedOrderIndex: 0,
            orderSequence: 1001,

            // Numpad state
            numpadMode: "qty", // 'qty' | 'discount' | 'price'
            numpadBuffer: "",

            get activeOrder() {
                if (!this.orders.length) {
                    this.createOrder();
                }
                return this.orders[this.selectedOrderIndex] || this.orders[0];
            },

            get selectedLine() {
                const order = this.activeOrder;
                if (!order || !order.lines.length) return null;
                const found = order.lines.find((l) => l.uuid === order.selectedLineUuid);
                return found || order.lines[order.lines.length - 1];
            },

            createOrder() {
                const newUid = String(this.orderSequence++);
                const order = {
                    uid: newUid,
                    id: false,
                    partner_id: false,
                    partner_name: "",
                    note: "",
                    lines: [],
                    selectedLineUuid: null,
                    payments: [],
                };
                this.orders.push(order);
                this.selectedOrderIndex = this.orders.length - 1;
                this.numpadMode = "qty";
                this.numpadBuffer = "";
                return order;
            },

            selectOrder(index) {
                if (index >= 0 && index < this.orders.length) {
                    this.selectedOrderIndex = index;
                    this.numpadBuffer = "";
                }
            },

            removeOrder(index) {
                if (this.orders.length <= 1) {
                    // Reset single order
                    this.orders = [];
                    this.createOrder();
                    return;
                }
                this.orders.splice(index, 1);
                if (this.selectedOrderIndex >= this.orders.length) {
                    this.selectedOrderIndex = this.orders.length - 1;
                }
                this.numpadBuffer = "";
            },

            selectLine(line) {
                if (this.activeOrder) {
                    this.activeOrder.selectedLineUuid = line ? line.uuid : null;
                    this.numpadBuffer = "";
                }
            },

            addProduct(product) {
                const order = this.activeOrder;
                const existing = order.lines.find((l) => l.product_id === product.id);
                if (existing) {
                    existing.qty += 1;
                    this.selectLine(existing);
                } else {
                    const newLine = {
                        uuid: "line_" + lineIdCounter++,
                        product_id: product.id,
                        name: product.name,
                        code: product.code || "",
                        qty: 1,
                        unit_price: product.price,
                        original_price: product.price,
                        discount: 0, // percent
                    };
                    order.lines.push(newLine);
                    this.selectLine(newLine);
                }
                this.numpadBuffer = "";
            },

            getProductQtyInCart(productId) {
                const order = this.activeOrder;
                if (!order) return 0;
                const line = order.lines.find((l) => l.product_id === productId);
                return line ? line.qty : 0;
            },

            setNumpadMode(mode) {
                this.numpadMode = mode;
                this.numpadBuffer = "";
            },

            handleNumpad(key) {
                const line = this.selectedLine;
                if (!line) return;

                if (key === "backspace") {
                    if (this.numpadBuffer.length > 0) {
                        this.numpadBuffer = this.numpadBuffer.slice(0, -1);
                    } else {
                        // If buffer empty, delete line or set qty to 0
                        this.removeLine(line);
                        return;
                    }
                } else if (key === "clear") {
                    this.numpadBuffer = "";
                } else if (key === "+/-") {
                    if (this.numpadMode === "qty") {
                        line.qty = -line.qty;
                        if (this.numpadBuffer) {
                            this.numpadBuffer = this.numpadBuffer.startsWith("-")
                                ? this.numpadBuffer.slice(1)
                                : "-" + this.numpadBuffer;
                        }
                    } else if (this.numpadMode === "price") {
                        line.unit_price = -line.unit_price;
                        if (this.numpadBuffer) {
                            this.numpadBuffer = this.numpadBuffer.startsWith("-")
                                ? this.numpadBuffer.slice(1)
                                : "-" + this.numpadBuffer;
                        }
                    }
                    return;
                } else if (key === "." || key === ",") {
                    if (!this.numpadBuffer.includes(".")) {
                        this.numpadBuffer = (this.numpadBuffer || "0") + ".";
                    }
                } else {
                    // Digits 0-9
                    this.numpadBuffer += key;
                }

                const value = parseFloat(this.numpadBuffer) || 0;

                if (this.numpadMode === "qty") {
                    line.qty = this.numpadBuffer === "" ? 1 : value;
                } else if (this.numpadMode === "discount") {
                    line.discount = Math.min(100, Math.max(0, value));
                } else if (this.numpadMode === "price") {
                    line.unit_price = Math.max(0, value);
                }
            },

            removeLine(line) {
                const order = this.activeOrder;
                order.lines = order.lines.filter((l) => l.uuid !== line.uuid);
                if (order.selectedLineUuid === line.uuid) {
                    order.selectedLineUuid = order.lines.length
                        ? order.lines[order.lines.length - 1].uuid
                        : null;
                }
                this.numpadBuffer = "";
            },

            setPartner(partner) {
                const order = this.activeOrder;
                if (partner) {
                    order.partner_id = partner.id;
                    order.partner_name = partner.name;
                } else {
                    order.partner_id = false;
                    order.partner_name = "";
                }
            },

            setNote(note) {
                if (this.activeOrder) {
                    this.activeOrder.note = note || "";
                }
            },

            getLineTotal(line) {
                const gross = (line.qty || 0) * (line.unit_price || 0);
                const discount = gross * ((line.discount || 0) / 100);
                return +(gross - discount).toFixed(2);
            },

            getOrderSubtotal() {
                const order = this.activeOrder;
                if (!order) return 0;
                return order.lines.reduce((sum, l) => sum + this.getLineTotal(l), 0);
            },

            getOrderTaxes() {
                // Approximate TVA based on 19% or company param
                const subtotal = this.getOrderSubtotal();
                return +(subtotal * 0.19).toFixed(2);
            },

            getOrderTotal() {
                const order = this.activeOrder;
                if (!order) return 0;
                // In Smail ecosystem, line totals are HT and total TTC includes TVA
                return this.getOrderSubtotal();
            },

            getPaidTotal() {
                const order = this.activeOrder;
                if (!order) return 0;
                return order.payments.reduce((sum, p) => sum + p.amount, 0);
            },

            getRemaining() {
                return Math.max(0, this.getOrderTotal() - this.getPaidTotal());
            },

            async loadData() {
                const data = await orm.call("sm_pos.session", "load_pos_data", [this.session.id]);
                this.config = data.config;
                this.user = data.user;
                this.company = data.company;
                this.products = data.products;
                this.categories = data.categories;
                this.partners = data.partners;
                this.paymentModes = data.payment_modes;
                this.recentOrders = data.recent_orders || [];
                if (!this.orders.length) {
                    this.createOrder();
                }
                return data;
            },

            async openSession(configId, openingCash) {
                const session = await orm.call("sm_pos.session", "open_session", [
                    configId,
                    openingCash,
                ]);
                this.session = session;
                await this.loadData();
                return session;
            },

            async closeSession(closingCash, notes) {
                const res = await orm.call("sm_pos.session", "close_session", [
                    this.session.id,
                    closingCash,
                    notes,
                ]);
                this.session = null;
                return res;
            },

            async startClosingControl() {
                const data = await orm.call("sm_pos.session", "start_closing_control", [
                    this.session.id,
                ]);
                this.session = data;
                return data;
            },

            async resumeSession() {
                const data = await orm.call("sm_pos.session", "resume_session", [
                    this.session.id,
                ]);
                this.session = data;
                return data;
            },

            async syncOrder() {
                const order = this.activeOrder;
                const orderPayload = {
                    id: order.id,
                    partner_id: order.partner_id,
                    note: order.note,
                    lines: order.lines.map((l) => ({
                        product_id: l.product_id,
                        name: l.name,
                        qty: l.qty,
                        unit_price: l.unit_price * (1 - (l.discount || 0) / 100),
                    })),
                };
                const res = await orm.call("sm_pos.session", "sync_pos_order", [
                    this.session.id,
                    orderPayload,
                ]);
                order.id = res.id;
                order.name = res.name;
                return res;
            },

            async addPayment(paymentMode, amount) {
                const order = this.activeOrder;
                const res = await orm.call("sm_pos.session", "add_payment", [
                    this.session.id,
                    order.id,
                    paymentMode.id,
                    amount,
                ]);
                order.payments.push({
                    payment_mode_id: paymentMode.id,
                    payment_mode_name: paymentMode.name,
                    amount: amount,
                });
                return res;
            },

            async getReceiptData(orderId) {
                return await orm.call("sm_pos.session", "get_receipt_data", [
                    this.session.id,
                    orderId || this.activeOrder.id,
                ]);
            },
        });

        return service;
    },
};

registry.category("services").add("pos", posService);