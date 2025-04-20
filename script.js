document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            if (this.getAttribute('href') !== '#') {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    // Close mobile menu if open
                    if (navLinks.classList.contains('active')) {
                        navLinks.classList.remove('active');
                    }
                    
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Legal documents handling
    const termsLink = document.getElementById('terms-link');
    const privacyLink = document.getElementById('privacy-link');
    
    if (termsLink) {
        termsLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = 'terms.html';
        });
    }
    
    if (privacyLink) {
        privacyLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = 'privacy.html';
        });
    }
    
    // Also update the link in the download section
    const downloadTermsLink = document.querySelector('.download-note a');
    if (downloadTermsLink) {
        downloadTermsLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = 'terms.html';
        });
    }
    
    // FAQ accordion
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', () => {
            // Close all other FAQ items
            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle current FAQ item
            item.classList.toggle('active');
        });
    });
    
    // Migliorata l'animazione on scroll per evitare che gli elementi scompaiano
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.feature-card, .download-content, .app-preview, .faq-item');
        
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight - 100) {
                element.classList.add('visible');
                
                // Assicuriamoci che l'elemento rimanga visibile
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };
    
    // Modificato il setup delle animazioni per renderle più stabili
    const setupAnimations = () => {
        const elements = document.querySelectorAll('.feature-card, .download-content, .app-preview, .faq-item');
        
        elements.forEach((element, index) => {
            // Impostare l'opacità iniziale e la trasformazione
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            // Aggiunto un piccolo ritardo basato sull'indice per creare un effetto a cascata
            element.style.transitionDelay = `${index * 0.1}s`;
        });
        
        // Aggiungi la classe visible agli elementi
        document.addEventListener('scroll', animateOnScroll);
        
        // Prima chiamata per mostrare gli elementi già visibili all'avvio
        setTimeout(animateOnScroll, 300);
    };
    
    setupAnimations();
    
    // Download button effect
    const downloadBtn = document.querySelector('.download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            // Add a visual feedback that the download started
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
            
            // Reset the button text after 2 seconds
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-download"></i> Download YTDLPY';
            }, 2000);
        });
    }
    
    // Add loading animation to the page
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
    });
    
    // Parallax effect to hero section, ottimizzato per evitare problemi di scroll
    let ticking = false;
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                const scrollPosition = window.scrollY;
                const heroSection = document.querySelector('.hero');
                const heroImage = document.querySelector('.hero-image');
                
                if (heroSection && heroImage && scrollPosition < heroSection.offsetHeight) {
                    heroImage.style.transform = `translateY(${scrollPosition * 0.05}px)`;
                }
                ticking = false;
            });
            ticking = true;
        }
    });

    // Aggiunta classe CSS per rimuovere gli elementi animati se non più visibili
    document.addEventListener('scroll', function() {
        // Applicare solo se sono già stati visibili una volta
        const animatedElements = document.querySelectorAll('.visible');
        animatedElements.forEach(element => {
            // Mantieni gli elementi visibili anche dopo l'animazione
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        });
    });
});
