// Main JavaScript for Sai Balusu's Personal Website

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('nav ul');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('nav') && !event.target.closest('.mobile-menu-btn')) {
            if (navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
            }
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                // Close mobile menu if open
                if (navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                }
                
                window.scrollTo({
                    top: targetElement.offsetTop - 70, // Adjust for header height
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Portfolio filtering
    const filterButtons = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');
    
    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                
                // Show/hide portfolio items based on filter
                portfolioItems.forEach(item => {
                    if (filter === 'all' || item.classList.contains(filter)) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // Form validation for contact form
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic validation
            let valid = true;
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const message = document.getElementById('message');
            
            // Reset error states
            [name, email, message].forEach(field => {
                field.classList.remove('error');
            });
            
            // Validate name
            if (!name.value.trim()) {
                name.classList.add('error');
                valid = false;
            }
            
            // Validate email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!email.value.trim() || !emailRegex.test(email.value.trim())) {
                email.classList.add('error');
                valid = false;
            }
            
            // Validate message
            if (!message.value.trim()) {
                message.classList.add('error');
                valid = false;
            }
            
            if (valid) {
                // Submit form via AJAX
                const formData = new FormData(contactForm);
                
                fetch('/contact', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show success message
                        const successMessage = document.createElement('div');
                        successMessage.className = 'success-message';
                        successMessage.textContent = 'Your message has been sent successfully!';
                        contactForm.reset();
                        contactForm.parentNode.insertBefore(successMessage, contactForm.nextSibling);
                        
                        // Remove success message after 5 seconds
                        setTimeout(() => {
                            successMessage.remove();
                        }, 5000);
                    } else {
                        // Show error message
                        const errorMessage = document.createElement('div');
                        errorMessage.className = 'error-message';
                        errorMessage.textContent = data.message || 'There was an error sending your message. Please try again.';
                        contactForm.parentNode.insertBefore(errorMessage, contactForm.nextSibling);
                        
                        // Remove error message after 5 seconds
                        setTimeout(() => {
                            errorMessage.remove();
                        }, 5000);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Show error message
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'error-message';
                    errorMessage.textContent = 'There was an error sending your message. Please try again.';
                    contactForm.parentNode.insertBefore(errorMessage, contactForm.nextSibling);
                    
                    // Remove error message after 5 seconds
                    setTimeout(() => {
                        errorMessage.remove();
                    }, 5000);
                });
            }
        });
    }
    
    // Admin panel functionality
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            fetch('/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/admin/dashboard';
                } else {
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'error-message';
                    errorMessage.textContent = data.message || 'Invalid credentials. Please try again.';
                    loginForm.parentNode.insertBefore(errorMessage, loginForm.nextSibling);
                    
                    setTimeout(() => {
                        errorMessage.remove();
                    }, 5000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
    
    // Resume upload preview
    const resumeUpload = document.getElementById('resume-upload');
    const resumePreview = document.getElementById('resume-preview');
    
    if (resumeUpload && resumePreview) {
        resumeUpload.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    resumePreview.innerHTML = `
                        <div class="preview-file">
                            <i class="fas fa-file-pdf"></i>
                            <span>${file.name}</span>
                        </div>
                    `;
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Scroll to top button
    const scrollTopBtn = document.getElementById('scroll-top');
    
    if (scrollTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollTopBtn.classList.add('show');
            } else {
                scrollTopBtn.classList.remove('show');
            }
        });
        
        scrollTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Animate elements on scroll
    const animateElements = document.querySelectorAll('.animate');
    
    if (animateElements.length > 0) {
        function checkIfInView() {
            animateElements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                const elementVisible = 150;
                
                if (elementTop < window.innerHeight - elementVisible) {
                    element.classList.add('active');
                }
            });
        }
        
        window.addEventListener('scroll', checkIfInView);
        checkIfInView(); // Check on page load
    }
});
