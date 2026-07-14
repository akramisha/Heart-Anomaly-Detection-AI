document.getElementById('reload-btn').addEventListener('click', () => {
    document.getElementById('patient-profile-form').reset();
    alert('Form has been reset!');
  });
  
  function validateForm() {
    // Get form values
    const fullName = document.getElementById('full-name').value;
    const newPassword = document.getElementById('new-password').value;
  
    // Validate Full Name (no digits allowed)
    const nameRegex = /\d/;
    if (nameRegex.test(fullName)) {
      alert('Full Name should not contain digits.');
      return false; // Prevent form submission
    }
  
    // Validate Password (at least 8 characters long)
    if (newPassword.length < 8) {
      alert('New Password must be at least 8 characters long.');
      return false; // Prevent form submission
    }
  
    // If all validations pass, allow the form to submit
    alert('Profile updated successfully!');
    return true;
  }
 // Check if the user is logged in when accessing the profile page
 