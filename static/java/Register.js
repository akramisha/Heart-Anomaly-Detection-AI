const form = document.getElementById('form');
const firstname_input = document.getElementById('firstname-input');
const email_input = document.getElementById('email-input');
const password_input = document.getElementById('password-input');
const repeat_password_input = document.getElementById('repeat-password-input');
const error_message = document.getElementById('error-message');

// Predefined valid login credentials (for demonstration purposes; replace with server-side validation in production)
const validLoginCredentials = {
  email: 'user@example.com',
  password: 'password123',
};

// Form submission handler
form.addEventListener('submit', (e) => {
  let errors = [];

  if (firstname_input) {
    // If we have a firstname input, this is a signup
    errors = getSignupFormErrors(
      firstname_input.value,
      email_input.value,
      password_input.value,
      repeat_password_input.value
    );
  } else {
    // If we don't have a firstname input, this is a login
    errors = getLoginFormErrors(email_input.value, password_input.value);
    if (errors.length === 0 && !validateLogin(email_input.value, password_input.value)) {
      errors.push('Invalid email or password');
    }
  }

  if (errors.length > 0) {
    // If there are any errors
    e.preventDefault();
    error_message.innerText = errors.join('. ');
  } else if (!firstname_input) {
    // Redirect for login if no errors (only for login scenario)
    window.location.href = 'dashboard.html'; // Replace with the actual dashboard page
  }
});

// Signup form validation
function getSignupFormErrors(firstname, email, password, repeatPassword) {
  let errors = [];

  if (firstname === '' || firstname == null) {
    errors.push('Firstname is required');
    firstname_input.parentElement.classList.add('incorrect');
  } else if (/\d/.test(firstname)) {
    errors.push('Firstname must not contain digits');
    firstname_input.parentElement.classList.add('incorrect');
  }
  if (email === '' || email == null) {
    errors.push('Email is required');
    email_input.parentElement.classList.add('incorrect');
  }
  if (password === '' || password == null) {
    errors.push('Password is required');
    password_input.parentElement.classList.add('incorrect');
  }
  if (password.length < 8) {
    errors.push('Password must have at least 8 characters');
    password_input.parentElement.classList.add('incorrect');
  }
  if (password !== repeatPassword) {
    errors.push('Password does not match repeated password');
    password_input.parentElement.classList.add('incorrect');
    repeat_password_input.parentElement.classList.add('incorrect');
  }

  return errors;
}

// Login form validation
function getLoginFormErrors(email, password) {
  let errors = [];

  if (email === '' || email == null) {
    errors.push('Email is required');
    email_input.parentElement.classList.add('incorrect');
  }
  if (password === '' || password == null) {
    errors.push('Password is required');
    password_input.parentElement.classList.add('incorrect');
  }

  return errors;
}

// Validate login credentials (mock function, replace with API call in production)
function validateLogin(email, password) {
  return email === validLoginCredentials.email && password === validLoginCredentials.password;
}

// Remove error styling and messages when input is corrected
const allInputs = [firstname_input, email_input, password_input, repeat_password_input].filter(input => input != null);

allInputs.forEach(input => {
  input.addEventListener('input', () => {
    if (input.parentElement.classList.contains('incorrect')) {
      input.parentElement.classList.remove('incorrect');
      error_message.innerText = '';
    }
  });
});
