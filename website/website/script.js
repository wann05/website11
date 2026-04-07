document.addEventListener('DOMContentLoaded', () => {
    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Mobile Menu Toggle
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');

    // Dynamic Admin Navbar Configuration
    const isAdmin = localStorage.getItem('isAdmin') === 'true';
    if (isAdmin && navMenu) {
        navMenu.innerHTML = `
            <a href="index.html" class="nav-link">Home</a>
            <a href="index.html#about" class="nav-link">About</a>
            <a href="organization.html" class="nav-link">Organization</a>
            <a href="orders.html" class="nav-link" style="color: var(--accent-primary); font-weight: 700;">Orders</a>
            <a href="members.html" class="nav-link" style="color: var(--accent-primary); font-weight: 700;">Members</a>
            <a href="#" class="nav-link btn-nav login-btn" id="logout-btn">Logout</a>
        `;
        document.getElementById('logout-btn').addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('isAdmin');
            window.location.href = 'index.html';
        });
    }

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            
            // Toggle hamburger icon animation
            const bars = document.querySelectorAll('.bar');
            if (navMenu.classList.contains('active')) {
                bars[0].style.transform = 'rotate(-45deg) translate(-5px, 6px)';
                bars[1].style.opacity = '0';
                bars[2].style.transform = 'rotate(45deg) translate(-5px, -6px)';
            } else {
                bars[0].style.transform = 'none';
                bars[1].style.opacity = '1';
                bars[2].style.transform = 'none';
            }
        });
    }

    // Checkout Form processing mapped to /api/checkout
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            // Assuming required fields match exactly index mapped selectors
            const payload = {
                quantity: checkoutForm.querySelector('input[type="number"]').value,
                full_name: checkoutForm.querySelectorAll('input[type="text"]')[0].value,
                email_address: checkoutForm.querySelector('input[type="email"]').value,
                phone_number: checkoutForm.querySelector('input[type="tel"]').value,
                shipping_address: checkoutForm.querySelectorAll('textarea')[0].value,
                payment_option: checkoutForm.querySelector('select').value,
                order_notes: checkoutForm.querySelectorAll('textarea')[1]?.value || ''
            };
            
            try {
                const res = await fetch('http://localhost:5000/api/checkout', {
                    method: 'POST',
                    body: JSON.stringify(payload),
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await res.json();
                if (data.success) {
                    // Success notification triggered natively per standard API architecture
                    alert("Success! Your checkout for Cable Pod was successfully placed. Your order has been saved.");
                    checkoutForm.reset();
                } else {
                    alert('Server error: ' + data.error);
                }
            } catch(error) {
                alert('Connection error. Please make sure server.py is running.');
            }
        });
    }

    // Join Form processing mapped to /api/join
    const joinForm = document.getElementById('registration-form');
    if (joinForm) {
        joinForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const inputs = joinForm.querySelectorAll('input');
            const payload = {
                first_name: inputs[0].value,
                last_name: inputs[1].value,
                email: inputs[2].value
            };
            
            try {
                const res = await fetch('http://localhost:5000/api/join', {
                    method: 'POST',
                    body: JSON.stringify(payload),
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await res.json();
                if (data.success) {
                    alert("Welcome! You have successfully joined the Alvoriya community.");
                    joinForm.reset();
                } else {
                    alert('Server error: ' + data.error);
                }
            } catch(error) {
                alert('Connection error. Please make sure server.py is running.');
            }
        });
    }

    // Custom Login implementation (Admin mapping)
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = loginForm.querySelector('input[type="email"]').value;
            const password = loginForm.querySelector('input[type="password"]').value;
            
            if (email === 'admin@gmail.com' && password === 'Admin') {
                localStorage.setItem('isAdmin', 'true');
                window.location.href = 'orders.html';
            } else {
                alert('Invalid Access. Admin restricted portal.');
            }
        });
    }

    // Auto-fetch data for Orders page
    if (window.location.pathname.includes('orders.html')) {
        const fetchOrders = async () => {
            const tableBody = document.getElementById('admin-table-body');
            if(!tableBody) return;
            try {
                const res = await fetch('http://localhost:5000/api/orders');
                const data = await res.json();
                if (data.success) {
                    if(data.data.length === 0) {
                        tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem;">No orders found.</td></tr>`;
                        return;
                    }
                    tableBody.innerHTML = data.data.map(order => `
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 1rem;">#${order.id}</td>
                            <td style="padding: 1rem;">${order.full_name}</td>
                            <td style="padding: 1rem;">${order.email_address}</td>
                            <td style="padding: 1rem;">${order.quantity} units</td>
                            <td style="padding: 1rem;">${order.payment_option.toUpperCase()}</td>
                            <td style="padding: 1rem;">${new Date(order.ordered_at).toLocaleString()}</td>
                        </tr>
                    `).join('');
                }
            } catch(e) {
                tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem; color: red;">Failed to connect backend.</td></tr>`;
            }
        };
        fetchOrders();
    }

    // Auto-fetch data for Members page
    if (window.location.pathname.includes('members.html')) {
        const fetchMembers = async () => {
            const tableBody = document.getElementById('admin-table-body');
            if(!tableBody) return;
            try {
                const res = await fetch('http://localhost:5000/api/members');
                const data = await res.json();
                if (data.success) {
                     if(data.data.length === 0) {
                        tableBody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 2rem;">No members found.</td></tr>`;
                        return;
                    }
                    tableBody.innerHTML = data.data.map(member => `
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 1rem;">#${member.id}</td>
                            <td style="padding: 1rem;">${member.first_name} ${member.last_name}</td>
                            <td style="padding: 1rem;">${member.email}</td>
                            <td style="padding: 1rem;">${new Date(member.applied_at).toLocaleString()}</td>
                        </tr>
                    `).join('');
                }
            } catch(e) {
                tableBody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 2rem; color: red;">Failed to connect backend.</td></tr>`;
            }
        };
        fetchMembers();
    }
});
