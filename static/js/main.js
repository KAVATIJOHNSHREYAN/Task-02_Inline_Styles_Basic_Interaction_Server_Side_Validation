/* ==========================================================================
   SMART CONTACT PORTAL V2 - INLINE CLIENT INTERACTION & VALIDATION ENGINE
   Features:
   - Live Email Validation
   - Live Password Strength Meter
   - Password Match Verification
   - Live Character Counter (Message)
   - Phone Formatting
   - File Upload Drag/Drop & Thumbnail Preview
   - Radio Card Activation
   - Dynamic Submit Button Enabler
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contactFormV2');
    if (!form) return;

    // Element References
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const emailFeedback = document.getElementById('emailFeedback');
    const phoneInput = document.getElementById('phone');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const passwordStrengthMeter = document.getElementById('passwordStrengthMeter');
    const passwordFeedback = document.getElementById('passwordFeedback');
    const confirmPasswordFeedback = document.getElementById('confirmPasswordFeedback');
    const messageInput = document.getElementById('message');
    const charCounter = document.getElementById('charCounter');
    const avatarInput = document.getElementById('avatar');
    const filePreview = document.getElementById('filePreview');
    const uploadPrompt = document.getElementById('uploadPrompt');
    const termsCheckbox = document.getElementById('terms');
    const submitBtn = document.getElementById('submitBtn');
    const radioCards = document.querySelectorAll('.radio-card');

    // 1. Live Email Validation
    if (emailInput && emailFeedback) {
        emailInput.addEventListener('input', () => {
            const val = emailInput.value.trim();
            const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;

            if (val === '') {
                emailFeedback.textContent = '';
                emailFeedback.className = 'field-feedback';
            } else if (emailRegex.test(val)) {
                emailFeedback.textContent = '✓ Valid email address format';
                emailFeedback.className = 'field-feedback valid';
            } else {
                emailFeedback.textContent = '✕ Enter a valid email (e.g. name@domain.com)';
                emailFeedback.className = 'field-feedback invalid';
            }
            checkFormValidity();
        });
    }

    // 2. Live Password Strength Meter
    if (passwordInput && passwordStrengthMeter && passwordFeedback) {
        passwordInput.addEventListener('input', () => {
            const val = passwordInput.value;
            let score = 0;

            if (val.length >= 8) score += 25;
            if (/[A-Z]/.test(val)) score += 25;
            if (/[0-9]/.test(val)) score += 25;
            if (/[^A-Za-z0-9]/.test(val)) score += 25;

            passwordStrengthMeter.style.width = `${score}%`;

            if (score === 0) {
                passwordStrengthMeter.style.backgroundColor = 'transparent';
                passwordFeedback.textContent = 'Minimum 8 characters with numbers & uppercase.';
                passwordFeedback.className = 'field-feedback';
            } else if (score <= 50) {
                passwordStrengthMeter.style.backgroundColor = '#F43F5E';
                passwordFeedback.textContent = 'Weak password';
                passwordFeedback.className = 'field-feedback invalid';
            } else if (score <= 75) {
                passwordStrengthMeter.style.backgroundColor = '#F59E0B';
                passwordFeedback.textContent = 'Moderate password strength';
                passwordFeedback.className = 'field-feedback';
            } else {
                passwordStrengthMeter.style.backgroundColor = '#10B981';
                passwordFeedback.textContent = '✓ Strong password';
                passwordFeedback.className = 'field-feedback valid';
            }

            validatePasswordMatch();
            checkFormValidity();
        });
    }

    // 3. Password Match Indicator
    function validatePasswordMatch() {
        if (!confirmPasswordInput || !confirmPasswordFeedback) return;
        const pass = passwordInput ? passwordInput.value : '';
        const confirmPass = confirmPasswordInput.value;

        if (confirmPass === '') {
            confirmPasswordFeedback.textContent = '';
            confirmPasswordFeedback.className = 'field-feedback';
        } else if (pass === confirmPass) {
            confirmPasswordFeedback.textContent = '✓ Passwords match';
            confirmPasswordFeedback.className = 'field-feedback valid';
        } else {
            confirmPasswordFeedback.textContent = '✕ Passwords do not match';
            confirmPasswordFeedback.className = 'field-feedback invalid';
        }
    }

    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', () => {
            validatePasswordMatch();
            checkFormValidity();
        });
    }

    // 4. Live Message Character Counter
    if (messageInput && charCounter) {
        const maxChars = 500;
        messageInput.addEventListener('input', () => {
            const currentLen = messageInput.value.length;
            charCounter.textContent = `${currentLen} / ${maxChars} characters`;

            if (currentLen > maxChars) {
                charCounter.style.color = '#F43F5E';
            } else if (currentLen >= 10) {
                charCounter.style.color = '#10B981';
            } else {
                charCounter.style.color = '#94A3B8';
            }
            checkFormValidity();
        });
    }

    // 5. Phone Formatting (Allows +, digits, spaces)
    if (phoneInput) {
        phoneInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/[^0-9+ ]/g, '');
            e.target.value = val;
            checkFormValidity();
        });
    }

    // 6. Radio Card Active State Toggle
    radioCards.forEach(card => {
        card.addEventListener('click', () => {
            radioCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            const radio = card.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
            checkFormValidity();
        });
    });

    // 7. File Upload Preview & Drag-Drop
    if (avatarInput) {
        avatarInput.addEventListener('change', handleFileSelect);
    }

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                if (filePreview) {
                    filePreview.src = event.target.result;
                    filePreview.style.display = 'block';
                }
                if (uploadPrompt) {
                    uploadPrompt.textContent = `Selected: ${file.name}`;
                }
            };
            reader.readAsDataURL(file);
        }
    }

    // 8. Dynamic Submit Button State Handling
    function checkFormValidity() {
        if (!submitBtn || !termsCheckbox) return;

        const isTermsChecked = termsCheckbox.checked;
        const isNameValid = nameInput && nameInput.value.trim().length >= 2;
        const isEmailValid = emailInput && /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/.test(emailInput.value.trim());
        const rawPhone = phoneInput ? phoneInput.value.replace(/[^0-9]/g, '') : '';
        const isPhoneValid = rawPhone.length >= 7 && rawPhone.length <= 15;
        const isPassValid = passwordInput && passwordInput.value.length >= 8;
        const isMatchValid = confirmPasswordInput && confirmPasswordInput.value === passwordInput.value;
        const isMsgValid = messageInput && messageInput.value.trim().length >= 10;

        if (isTermsChecked && isNameValid && isEmailValid && isPhoneValid && isPassValid && isMatchValid && isMsgValid) {
            submitBtn.removeAttribute('disabled');
        } else {
            submitBtn.setAttribute('disabled', 'true');
        }
    }

    if (termsCheckbox) {
        termsCheckbox.addEventListener('change', checkFormValidity);
    }

    // Initial validity check
    checkFormValidity();

    // Submit Loading State
    form.addEventListener('submit', () => {
        if (submitBtn) {
            submitBtn.innerHTML = `
                <span class="spinner" style="display:inline-block; width:16px; height:16px; border:2px solid rgba(255,255,255,0.3); border-top-color:#fff; border-radius:50%; animation: spin 0.8s linear infinite;"></span>
                Processing Submission...
            `;
        }
    });
});

// Keyframe animation for spinner
const style = document.createElement('style');
style.innerHTML = `
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;
document.head.appendChild(style);
