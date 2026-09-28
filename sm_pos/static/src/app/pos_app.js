/** @odoo-module **/
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ProductCard } from "../components/product_card";
import { OrderLine } from "../components/order_line";
import { Numpad } from "../components/numpad";

export class PosApp extends Component {
    static template = "sm_pos.PosApp";
    static components = { ProductCard, OrderLine, Numpad };

    setup() {
        this.pos = useService("pos");
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            // Navigation
            activeTab: "caisse", // 'caisse' | 'commandes'
            
            // Search & Category
            searchTerm: "",
            selectedCategoryId: false,

            // Modals
            showPaymentModal: false,
            showClientModal: false,
            showNoteModal: false,
            showClosingModal: false,
            showReceiptModal: false,
            showStartSessionModal: false,
            showMenuDropdown: false,

            // Session opening state
            configs: [],
            selectedConfigId: false,
            openingCash: 0,
            sessionLoading: false,
            sessionError: false,

            // Payment modal state
            selectedPaymentMode: null,
            paymentAmountInput: "",
            paying: false,
            paymentError: false,

            // Receipt state
            lastReceiptData: null,

            // Note modal state
            currentNote: "",

            // Client modal state
            clientSearch: "",

            // Closing modal state
            countedCash: 0,
            closingNotes: "",
            closingLoading: false,
            closingData: null,

            // Barcode scan buffer
            barcodeBuffer: "",
            barcodeLastTime: 0,
        });

        this._onKeyDown = this._onKeyDown.bind(this);

        onMounted(async () => {
            window.addEventListener("keydown", this._onKeyDown);
            await this._initPos();
        });

        onWillUnmount(() => {
            window.removeEventListener("keydown", this._onKeyDown);
        });
    }

    // ------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------
    async _initPos() {
        this.state.sessionLoading = true;
        try {
            // Check for already active session
            const openSessions = await this.orm.searchRead(
                "sm_pos.session",
                [["state", "in", ["opening_control", "opened", "closing_control"]]],
                ["id", "name", "config_id", "state"]
            );

            if (openSessions.length > 0) {
                const s = openSessions[0];
                this.pos.session = { id: s.id, name: s.name, state: s.state };
                await this.pos.loadData();
            } else {
                // Load configs for opening modal
                const configs = await this.orm.searchRead(
                    "sm_pos.config",
                    [["active", "=", true]],
                    ["id", "name", "boxe_id", "stock_id"]
                );
                this.state.configs = configs;
                if (configs.length) {
                    this.state.selectedConfigId = configs[0].id;
                }
                this.state.showStartSessionModal = true;
            }
        } catch (err) {
            console.error("POS init error:", err);
        } finally {
            this.state.sessionLoading = false;
        }
    }

    async startNewSession() {
        if (!this.state.selectedConfigId) return;
        this.state.sessionLoading = true;
        this.state.sessionError = false;
        try {
            await this.pos.openSession(this.state.selectedConfigId, this.state.openingCash);
            this.state.showStartSessionModal = false;
        } catch (err) {
            this.state.sessionError = err.message || "Impossible d'ouvrir la session.";
        } finally {
            this.state.sessionLoading = false;
        }
    }

    async cancelStartSession() {
        this.state.showStartSessionModal = false;
        this.state.sessionError = false;
        if (!this.pos.session || this.pos.session.state === "closed") {
            await this.exitPos();
        }
    }

    async exitPos() {
        this.state.showMenuDropdown = false;
        try {
            if (this.env.config?.breadcrumbs?.length > 1) {
                await this.action.restore();
                return;
            }
        } catch (err) {
            console.warn("Could not restore previous action from breadcrumbs:", err);
        }

        try {
            await this.action.restore();
            return;
        } catch (err) {
            console.warn("Could not restore controller stack:", err);
        }

        try {
            if (window.history.length > 1) {
                window.history.back();
            } else {
                await this.action.doAction("shakliyat.action_landing_page");
            }
        } catch (err) {
            console.warn("Could not navigate back in history:", err);
            await this.action.doAction("shakliyat.action_landing_page");
        }
    }

    // ------------------------------------------------------------------
    // Barcode scanner listener
    // ------------------------------------------------------------------
    _onKeyDown(e) {
        if (e.key === "Escape" && this.state.showStartSessionModal) {
            this.cancelStartSession();
            return;
        }

        // Ignore if user is typing in an input or textarea
        if (["INPUT", "TEXTAREA"].includes(e.target.tagName)) return;

        const now = Date.now();
        if (now - this.state.barcodeLastTime > 100) {
            this.state.barcodeBuffer = "";
        }
        this.state.barcodeLastTime = now;

        if (e.key === "Enter") {
            if (this.state.barcodeBuffer.length >= 3) {
                this._handleBarcodeScan(this.state.barcodeBuffer);
            }
            this.state.barcodeBuffer = "";
        } else if (e.key.length === 1) {
            this.state.barcodeBuffer += e.key;
        }
    }

    _handleBarcodeScan(code) {
        const clean = code.trim().toLowerCase();
        const found = this.pos.products.find(
            (p) => (p.code || "").toLowerCase() === clean || p.name.toLowerCase().includes(clean)
        );
        if (found) {
            this.pos.addProduct(found);
        }
    }

    // ------------------------------------------------------------------
    // Categories & Products Getters
    // ------------------------------------------------------------------
    get categories() {
        return this.pos.categories || [];
    }

    getCategoryColorClass(index) {
        const colors = ["cat_blue", "cat_pink", "cat_cyan", "cat_amber", "cat_purple", "cat_mint"];
        return colors[index % colors.length];
    }

    get filteredProducts() {
        let list = this.pos.products || [];
        if (this.state.selectedCategoryId) {
            list = list.filter((p) => p.categ_id === this.state.selectedCategoryId);
        }
        if (this.state.searchTerm) {
            const term = this.state.searchTerm.toLowerCase();
            list = list.filter(
                (p) =>
                    p.name.toLowerCase().includes(term) ||
                    (p.code || "").toLowerCase().includes(term)
            );
        }
        return list;
    }

    selectCategory(categoryId) {
        this.state.selectedCategoryId =
            this.state.selectedCategoryId === categoryId ? false : categoryId;
    }

    // ------------------------------------------------------------------
    // Multi-Orders Navigation
    // ------------------------------------------------------------------
    get orders() {
        return this.pos.orders;
    }

    get activeOrderIndex() {
        return this.pos.selectedOrderIndex;
    }

    get activeOrder() {
        return this.pos.activeOrder;
    }

    addNewOrder() {
        this.pos.createOrder();
    }

    switchOrder(index) {
        this.pos.selectOrder(index);
    }

    closeOrder(index, e) {
        if (e) e.stopPropagation();
        this.pos.removeOrder(index);
    }

    // ------------------------------------------------------------------
    // Cart & Line selection
    // ------------------------------------------------------------------
    onSelectLine(line) {
        this.pos.selectLine(line);
    }

    get selectedLine() {
        return this.pos.selectedLine;
    }

    get formattedTotal() {
        return this.pos.getOrderTotal().toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    get formattedTaxes() {
        return this.pos.getOrderTaxes().toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    get currency() {
        return (this.pos.company && this.pos.company.currency) || "$";
    }

    get cashierInitial() {
        const name = (this.pos.user && this.pos.user.name) || "A";
        return name.charAt(0).toUpperCase();
    }

    // ------------------------------------------------------------------
    // Actions: Payment, Client, Note, Menu
    // ------------------------------------------------------------------
    openPayment() {
        if (!this.activeOrder.lines.length) return;
        this.state.selectedPaymentMode = this.pos.paymentModes.length
            ? this.pos.paymentModes[0]
            : null;
        this.state.paymentAmountInput = this.pos.getOrderTotal().toFixed(2);
        this.state.paymentError = false;
        this.state.showPaymentModal = true;
    }

    closePayment() {
        this.state.showPaymentModal = false;
    }

    get paymentChange() {
        const inputVal = parseFloat(this.state.paymentAmountInput) || 0;
        return Math.max(0, inputVal - this.pos.getOrderTotal());
    }

    setQuickCash(amount) {
        this.state.paymentAmountInput = Number(amount).toFixed(2);
    }

    addQuickCash(amount) {
        const current = parseFloat(this.state.paymentAmountInput) || 0;
        this.state.paymentAmountInput = (current + amount).toFixed(2);
    }

    async validatePayment(withReceipt = true) {
        if (!this.state.selectedPaymentMode) {
            this.state.paymentError = "Veuillez sélectionner un mode de paiement.";
            return;
        }
        const total = this.pos.getOrderTotal();
        const paidInput = parseFloat(this.state.paymentAmountInput) || 0;
        if (paidInput <= 0) {
            this.state.paymentError = "Veuillez entrer un montant valide.";
            return;
        }

        this.state.paying = true;
        this.state.paymentError = false;
        try {
            // 1. Sync order to sm_sales.order
            const orderRes = await this.pos.syncOrder();

            // 2. Add payment (only record up to order total in cash drawer to keep cash balance exact)
            const allocatedAmount = Math.min(paidInput, total);
            await this.pos.addPayment(this.state.selectedPaymentMode, allocatedAmount);

            // 3. Receipt preparation
            if (withReceipt) {
                const receiptData = await this.pos.getReceiptData(orderRes.id);
                receiptData.paid_amount = paidInput;
                receiptData.change = Math.max(0, paidInput - total);
                receiptData.mode_name = this.state.selectedPaymentMode.name;
                this.state.lastReceiptData = receiptData;
                this.state.showReceiptModal = true;
            }

            // 4. Close payment modal & reset/switch order
            this.state.showPaymentModal = false;
            this.pos.removeOrder(this.activeOrderIndex);

            // 5. Auto print if receipt requested
            if (withReceipt) {
                setTimeout(() => {
                    this.printReceipt();
                }, 300);
            }
        } catch (err) {
            this.state.paymentError = err.message || "Échec du règlement.";
        } finally {
            this.state.paying = false;
        }
    }

    printReceipt() {
        window.print();
    }

    closeReceipt() {
        this.state.showReceiptModal = false;
    }

    // ------------------------------------------------------------------
    // Client selection modal
    // ------------------------------------------------------------------
    openClientModal() {
        this.state.clientSearch = "";
        this.state.showClientModal = true;
    }

    closeClientModal() {
        this.state.showClientModal = false;
    }

    get filteredPartners() {
        const term = (this.state.clientSearch || "").toLowerCase();
        if (!term) return this.pos.partners || [];
        return (this.pos.partners || []).filter(
            (p) =>
                p.name.toLowerCase().includes(term) ||
                (p.phone && p.phone.toLowerCase().includes(term))
        );
    }

    choosePartner(partner) {
        this.pos.setPartner(partner);
        this.closeClientModal();
    }

    // ------------------------------------------------------------------
    // Note modal
    // ------------------------------------------------------------------
    openNoteModal() {
        this.state.currentNote = this.activeOrder.note || "";
        this.state.showNoteModal = true;
    }

    closeNoteModal() {
        this.state.showNoteModal = false;
    }

    saveNote() {
        this.pos.setNote(this.state.currentNote);
        this.closeNoteModal();
    }

    // ------------------------------------------------------------------
    // Session closing modal
    // ------------------------------------------------------------------
    async openClosingModal() {
        this.state.showMenuDropdown = false;
        this.state.closingLoading = true;
        this.state.showClosingModal = true;
        try {
            const data = await this.pos.startClosingControl();
            this.state.closingData = data;
            this.state.countedCash = data.cash_register_balance_end || 0;
            this.state.closingNotes = "";
        } catch (err) {
            console.error("Failed to load closing data:", err);
        } finally {
            this.state.closingLoading = false;
        }
    }

    closeClosingModal() {
        this.pos.resumeSession();
        this.state.showClosingModal = false;
    }

    get closingDifference() {
        const theoretical = (this.state.closingData && this.state.closingData.cash_register_balance_end) || 0;
        return Number(this.state.countedCash) - theoretical;
    }

    async confirmCloseSession() {
        this.state.closingLoading = true;
        try {
            await this.pos.closeSession(this.state.countedCash, this.state.closingNotes);
            this.state.showClosingModal = false;
            // Show opening modal for new session
            this.state.showStartSessionModal = true;
        } catch (err) {
            console.error("Close session error:", err);
        } finally {
            this.state.closingLoading = false;
        }
    }

    toggleMenuDropdown() {
        this.state.showMenuDropdown = !this.state.showMenuDropdown;
    }

    switchTab(tab) {
        this.state.activeTab = tab;
    }

    clearSearch() {
        this.state.searchTerm = "";
    }

    clearActiveCart() {
        if (this.activeOrder) {
            this.activeOrder.lines = [];
        }
    }

    async reprintOrderReceipt(orderId) {
        const data = await this.pos.getReceiptData(orderId);
        this.state.lastReceiptData = data;
        this.state.showReceiptModal = true;
    }
}

registry.category("actions").add("sm_pos.pos_app", PosApp);