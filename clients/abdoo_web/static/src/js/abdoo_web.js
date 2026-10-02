// Abdoo Web E-Commerce Client Logic
(function () {
    'use strict';

    if (window.__ABDOO_WEB_JS_INITIALIZED__) {
        return;
    }
    window.__ABDOO_WEB_JS_INITIALIZED__ = true;

    const STORAGE_KEY = 'abdoo_web_cart_v1';

    // Utilitaires de stockage LocalStorage
    function getCart() {
        try {
            const data = localStorage.getItem(STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Erreur lecture localStorage:', e);
            return [];
        }
    }

    function saveCart(cart) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
        } catch (e) {
            console.error('Erreur sauvegarde localStorage:', e);
        }
    }

    // Récupérer la configuration injectée par le serveur
    function getConfig() {
        const configElem = document.getElementById('abdoo-catalog-config');
        if (configElem) {
            try {
                return JSON.parse(configElem.textContent);
            } catch (e) {
                console.error('Erreur parsing config:', e);
            }
        }
        return { can_see_prices: false, is_logged_in: false, customer_info: {} };
    }

    // Animation du badge panier
    function animateCartBadge() {
        document.querySelectorAll('.abdoo-cart-count, #cart-drawer-count').forEach(badge => {
            badge.classList.remove('animate-bounce');
            void badge.offsetWidth; // trigger reflow
            badge.classList.add('animate-bounce');
        });
    }

    // Mise à jour de l'affichage du panier (badges, liste tiroir, totaux)
    function updateCartUI() {
        const cart = getCart();
        const config = getConfig();
        const totalCount = cart.reduce((sum, item) => sum + (parseInt(item.quantity, 10) || 1), 0);

        // Mise à jour de tous les badges du panier sur la page
        document.querySelectorAll('.abdoo-cart-count, #cart-drawer-count, #cart-badge-count, #floating-badge-count').forEach(elem => {
            elem.textContent = totalCount;
        });

        const listContainer = document.getElementById('cart-items-list');
        const footerSection = document.getElementById('cart-footer-section');
        const totalAmountElem = document.getElementById('cart-total-amount');

        if (!listContainer) return;

        if (cart.length === 0) {
            listContainer.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="fa fa-shopping-basket fa-3x mb-3 opacity-25"></i>
                    <h6 class="fw-bold">Votre panier est vide</h6>
                    <p class="small text-muted">Parcourez le catalogue et ajoutez des articles à votre panier.</p>
                </div>
            `;
            if (footerSection) {
                const submitBtns = footerSection.querySelectorAll('#btn-save-preorder, #btn-email-preorder, #btn-clear-cart');
                submitBtns.forEach(btn => btn.setAttribute('disabled', 'disabled'));
            }
            if (totalAmountElem) totalAmountElem.textContent = '0.00';
            return;
        }

        if (footerSection) {
            const submitBtns = footerSection.querySelectorAll('#btn-save-preorder, #btn-email-preorder, #btn-clear-cart');
            submitBtns.forEach(btn => btn.removeAttribute('disabled'));
        }

        let totalAmount = 0.0;
        let html = '';

        cart.forEach((item, index) => {
            const itemQty = parseInt(item.quantity, 10) || 1;
            const itemPrice = parseFloat(item.price) || 0.0;
            const itemSubtotal = itemPrice * itemQty;
            totalAmount += itemSubtotal;

            html += `
                <div class="abdoo-cart-item d-flex align-items-center gap-2 mb-2 p-2 border rounded-3 bg-white shadow-sm">
                    <img src="${item.img || '/web/static/img/placeholder.png'}"
                         class="abdoo-cart-item-img"
                         alt="${item.name}"
                         style="width: 48px; height: 48px; object-fit: contain; background: #f8fafc; border-radius: 6px; padding: 2px;">
                    <div class="flex-grow-1 min-w-0">
                        <div class="fw-bold small text-truncate text-dark" title="${item.name}">${item.name}</div>
                        ${item.code ? `<div class="text-muted" style="font-size: 0.75rem;">Réf: ${item.code}</div>` : ''}
                        ${config.can_see_prices ? `<div class="text-primary fw-bold small">${itemPrice.toFixed(2)}</div>` : ''}
                    </div>
                    <div class="d-flex align-items-center gap-1">
                        <div class="input-group input-group-sm" style="width: 95px;">
                            <button class="btn btn-outline-secondary btn-cart-minus px-2" data-index="${index}" type="button">-</button>
                            <input type="number"
                                   class="form-control text-center px-1 fw-bold input-cart-qty"
                                   data-index="${index}"
                                   value="${itemQty}"
                                   min="1"
                                   max="999"
                                   style="font-size: 0.85rem;"/>
                            <button class="btn btn-outline-secondary btn-cart-plus px-2" data-index="${index}" type="button">+</button>
                        </div>
                        <button class="btn btn-link btn-sm text-danger p-1 btn-cart-remove" data-index="${index}" title="Supprimer">
                            <i class="fa fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });

        listContainer.innerHTML = html;

        if (totalAmountElem) {
            totalAmountElem.textContent = totalAmount.toFixed(2);
        }
    }

    // Ajouter un produit au panier
    function addToCart(product) {
        if (!product || !product.id || isNaN(product.id)) {
            console.error('Article invalide pour le panier:', product);
            return;
        }

        let cart = getCart();
        const existingIndex = cart.findIndex(item => item.id === product.id);

        if (existingIndex > -1) {
            cart[existingIndex].quantity += product.quantity;
        } else {
            cart.push(product);
        }

        saveCart(cart);
        updateCartUI();
        animateCartBadge();
    }

    // Gestion du tiroir Offcanvas Cart
    function openCartOffcanvas() {
        const offcanvasEl = document.getElementById('abdooCartOffcanvas');
        if (!offcanvasEl) return;

        // Déplacer l'offcanvas directement sur le body pour sortir du stacking context #wrapwrap
        if (offcanvasEl.parentElement !== document.body) {
            document.body.appendChild(offcanvasEl);
        }

        if (window.bootstrap && window.bootstrap.Offcanvas) {
            try {
                const bsOffcanvas = window.bootstrap.Offcanvas.getOrCreateInstance(offcanvasEl);
                bsOffcanvas.show();
                return;
            } catch (e) {
                console.warn('Bootstrap Offcanvas failed, using fallback:', e);
            }
        }

        // Fallback natif si bootstrap n'est pas prêt
        offcanvasEl.classList.add('show');
        offcanvasEl.style.visibility = 'visible';
        let backdrop = document.getElementById('abdoo-cart-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.id = 'abdoo-cart-backdrop';
            backdrop.className = 'offcanvas-backdrop fade show';
            backdrop.addEventListener('click', closeCartOffcanvas);
            document.body.appendChild(backdrop);
        }
    }

    function closeCartOffcanvas() {
        const offcanvasEl = document.getElementById('abdooCartOffcanvas');
        if (!offcanvasEl) return;

        if (window.bootstrap && window.bootstrap.Offcanvas) {
            try {
                const bsOffcanvas = window.bootstrap.Offcanvas.getInstance(offcanvasEl);
                if (bsOffcanvas) bsOffcanvas.hide();
            } catch (e) {
                // ignore
            }
        }

        offcanvasEl.classList.remove('show');
        offcanvasEl.style.visibility = '';
        const backdrop = document.getElementById('abdoo-cart-backdrop');
        if (backdrop) backdrop.remove();
        document.querySelectorAll('.offcanvas-backdrop').forEach(el => el.remove());
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }

    // Soumission de la pré-commande
    async function submitPreOrder(actionType) {
        const cart = getCart();
        if (cart.length === 0) {
            alert('Votre panier est vide.');
            return;
        }

        const nameInput = document.getElementById('order-customer-name');
        const phoneInput = document.getElementById('order-customer-phone');
        const emailInput = document.getElementById('order-customer-email');
        const companyInput = document.getElementById('order-customer-company');
        const notesInput = document.getElementById('order-customer-notes');

        const customerName = nameInput ? nameInput.value.trim() : '';
        const customerPhone = phoneInput ? phoneInput.value.trim() : '';
        const customerEmail = emailInput ? emailInput.value.trim() : '';
        const customerCompany = companyInput ? companyInput.value.trim() : '';
        const notes = notesInput ? notesInput.value.trim() : '';

        if (!customerName) {
            alert('Veuillez renseigner votre nom complet.');
            if (nameInput) nameInput.focus();
            return;
        }

        if (!customerPhone) {
            alert('Veuillez renseigner votre numéro de téléphone.');
            if (phoneInput) phoneInput.focus();
            return;
        }

        if (actionType === 'email' && !customerEmail) {
            alert('Une adresse email est requise pour envoyer la pré-commande par email.');
            if (emailInput) emailInput.focus();
            return;
        }

        const btnActive = actionType === 'save'
            ? document.getElementById('btn-save-preorder')
            : document.getElementById('btn-email-preorder');

        const origBtnText = btnActive ? btnActive.innerHTML : '';
        if (btnActive) {
            btnActive.disabled = true;
            btnActive.innerHTML = '<i class="fa fa-spinner fa-spin me-1"></i> Traitement en cours...';
        }

        const payload = {
            customer_name: customerName,
            customer_phone: customerPhone,
            customer_email: customerEmail,
            customer_company: customerCompany,
            notes: notes,
            action_type: actionType,
            lines: cart.map(item => ({
                product_id: item.id,
                quantity: item.quantity,
                price: item.price,
                description: item.name,
            })),
        };

        try {
            const response = await fetch('/catalog/pre_order/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: payload,
                }),
            });

            const resultData = await response.json();
            const result = resultData.result || resultData;

            if (result && result.success) {
                // Vider le panier
                saveCart([]);
                updateCartUI();
                closeCartOffcanvas();

                // Afficher modal de succès
                const modalEl = document.getElementById('abdooOrderSuccessModal');
                const refElem = document.getElementById('success-modal-ref');
                const msgElem = document.getElementById('success-modal-message');

                if (refElem) refElem.textContent = result.order_name || 'Nouveau';
                if (msgElem) {
                    if (actionType === 'email') {
                        msgElem.textContent = 'Votre pré-commande a été enregistrée et un email de confirmation vous a été envoyé.';
                    } else {
                        msgElem.textContent = 'Votre pré-commande a bien été enregistrée dans notre système.';
                    }
                }

                if (modalEl && window.bootstrap && window.bootstrap.Modal) {
                    const bsModal = window.bootstrap.Modal.getOrCreateInstance(modalEl);
                    bsModal.show();
                } else {
                    alert('Pré-commande enregistrée avec succès ! Référence : ' + (result.order_name || ''));
                }
            } else {
                alert('Erreur: ' + ((result && result.error) || 'Impossible d\'enregistrer la pré-commande.'));
            }
        } catch (err) {
            console.error('Erreur lors de la soumission de la pré-commande:', err);
            alert('Une erreur réseau est survenue lors de l\'enregistrement de votre commande.');
        } finally {
            if (btnActive) {
                btnActive.disabled = false;
                btnActive.innerHTML = origBtnText;
            }
        }
    }

    // Enregistrement des écouteurs d'événements
    function initListeners() {
        if (window.__ABDOO_WEB_LISTENERS_INITIALIZED__) return;
        window.__ABDOO_WEB_LISTENERS_INITIALIZED__ = true;

        let lastQtyClickTime = 0;
        let lastAddClickTime = 0;

        document.addEventListener('click', function (e) {
            const now = Date.now();

            // Bouton + (incrémenter sur la fiche produit)
            const plusBtn = e.target.closest('.btn-qty-plus');
            if (plusBtn) {
                e.preventDefault();
                e.stopPropagation();
                if (now - lastQtyClickTime < 150) return;
                lastQtyClickTime = now;

                const picker = plusBtn.closest('.abdoo-qty-picker') || plusBtn.parentElement;
                const input = picker ? picker.querySelector('.input-product-qty') : null;
                if (input) {
                    const currentVal = parseInt(input.value, 10) || 1;
                    input.value = Math.max(1, currentVal + 1);
                }
                return;
            }

            // Bouton - (décrémenter sur la fiche produit)
            const minusBtn = e.target.closest('.btn-qty-minus');
            if (minusBtn) {
                e.preventDefault();
                e.stopPropagation();
                if (now - lastQtyClickTime < 150) return;
                lastQtyClickTime = now;

                const picker = minusBtn.closest('.abdoo-qty-picker') || minusBtn.parentElement;
                const input = picker ? picker.querySelector('.input-product-qty') : null;
                if (input) {
                    const currentVal = parseInt(input.value, 10) || 1;
                    input.value = Math.max(1, currentVal - 1);
                }
                return;
            }

            // Bouton "Ajouter au panier"
            const addBtn = e.target.closest('.btn-add-to-cart');
            if (addBtn) {
                e.preventDefault();
                e.stopPropagation();
                if (now - lastAddClickTime < 400) return;
                lastAddClickTime = now;

                const card = addBtn.closest('.abdoo-product-card');
                const qtyInput = card ? card.querySelector('.input-product-qty') : null;
                const quantity = Math.max(1, parseInt(qtyInput ? qtyInput.value : 1, 10));

                const product = {
                    id: parseInt(addBtn.dataset.productId, 10),
                    name: addBtn.dataset.productName || 'Article',
                    code: addBtn.dataset.productCode || '',
                    price: parseFloat(addBtn.dataset.productPrice || 0),
                    img: addBtn.dataset.productImg || '',
                    quantity: quantity,
                };

                addToCart(product);

                // Réinitialiser la quantité sur la carte produit à 1
                if (qtyInput) {
                    qtyInput.value = 1;
                }

                // Feedback visuel sur le bouton
                const origHtml = addBtn.innerHTML;
                addBtn.innerHTML = '<i class="fa fa-check me-1"></i> Ajouté !';
                addBtn.classList.replace('btn-primary', 'btn-success');
                setTimeout(() => {
                    addBtn.innerHTML = origHtml;
                    addBtn.classList.replace('btn-success', 'btn-primary');
                }, 1000);
                return;
            }

            // Bouton + dans le panier tiroir
            const cartPlusBtn = e.target.closest('.btn-cart-plus');
            if (cartPlusBtn) {
                e.preventDefault();
                const idx = parseInt(cartPlusBtn.dataset.index, 10);
                let cart = getCart();
                if (cart[idx]) {
                    cart[idx].quantity += 1;
                    saveCart(cart);
                    updateCartUI();
                }
                return;
            }

            // Bouton - dans le panier tiroir
            const cartMinusBtn = e.target.closest('.btn-cart-minus');
            if (cartMinusBtn) {
                e.preventDefault();
                const idx = parseInt(cartMinusBtn.dataset.index, 10);
                let cart = getCart();
                if (cart[idx]) {
                    if (cart[idx].quantity > 1) {
                        cart[idx].quantity -= 1;
                    } else {
                        cart.splice(idx, 1);
                    }
                    saveCart(cart);
                    updateCartUI();
                }
                return;
            }

            // Supprimer une ligne du panier
            const cartRemoveBtn = e.target.closest('.btn-cart-remove');
            if (cartRemoveBtn) {
                e.preventDefault();
                const idx = parseInt(cartRemoveBtn.dataset.index, 10);
                let cart = getCart();
                cart.splice(idx, 1);
                saveCart(cart);
                updateCartUI();
                return;
            }

            // Vider le panier
            if (e.target.closest('#btn-clear-cart')) {
                e.preventDefault();
                if (confirm('Êtes-vous sûr de vouloir vider le panier ?')) {
                    saveCart([]);
                    updateCartUI();
                }
                return;
            }

            // Ouvrir le panier
            if (e.target.closest('#btn-open-cart') || e.target.closest('#btn-floating-cart')) {
                e.preventDefault();
                openCartOffcanvas();
                return;
            }

            // Fermer le panier via les boutons fermer
            if (e.target.closest('[data-bs-dismiss="offcanvas"]')) {
                closeCartOffcanvas();
                return;
            }
        });

        // Changement direct de la quantité dans le panier via saisie
        document.addEventListener('change', function (e) {
            const cartQtyInput = e.target.closest('.input-cart-qty');
            if (cartQtyInput) {
                const idx = parseInt(cartQtyInput.dataset.index, 10);
                const newQty = Math.max(1, parseInt(cartQtyInput.value, 10) || 1);
                let cart = getCart();
                if (cart[idx]) {
                    cart[idx].quantity = newQty;
                    saveCart(cart);
                    updateCartUI();
                }
            }
        });

        // Envoi ou Sauvegarde de la pré-commande
        const btnSave = document.getElementById('btn-save-preorder');
        const btnEmail = document.getElementById('btn-email-preorder');

        if (btnSave) {
            btnSave.addEventListener('click', (e) => {
                e.preventDefault();
                submitPreOrder('save');
            });
        }
        if (btnEmail) {
            btnEmail.addEventListener('click', (e) => {
                e.preventDefault();
                submitPreOrder('email');
            });
        }
    }

    function start() {
        const offcanvasEl = document.getElementById('abdooCartOffcanvas');
        if (offcanvasEl && offcanvasEl.parentElement !== document.body) {
            document.body.appendChild(offcanvasEl);
        }
        const modalEl = document.getElementById('abdooOrderSuccessModal');
        if (modalEl && modalEl.parentElement !== document.body) {
            document.body.appendChild(modalEl);
        }
        updateCartUI();
        initListeners();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }

})();
