const dashboardUrl = 'SKU WISE AD SPEND.html';
const loginForm = document.getElementById('loginForm');
const errorMessage = document.getElementById('errorMessage');

const showError = (message) => {
  errorMessage.textContent = message;
  errorMessage.classList.remove('is-hidden');
};

const clearError = () => {
  errorMessage.textContent = '';
  errorMessage.classList.add('is-hidden');
};

const hashPassword = async (password) => {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hashBuffer))
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
};

const authenticateUser = async (username, password) => {
  const response = await fetch('users.json', { cache: 'no-store' });
  if (!response.ok) {
    throw new Error('Unable to load users.');
  }
  const users = await response.json();
  const hashedPassword = await hashPassword(password);
  return users.some((user) => user.username === username && user.password === hashedPassword);
};

const redirectToDashboard = () => {
  window.location.href = dashboardUrl;
};

if (sessionStorage.getItem('isAuthenticated') === 'true') {
  redirectToDashboard();
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearError();

  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  if (!username || !password) {
    showError('Please enter both username and password.');
    return;
  }

  try {
    const isValid = await authenticateUser(username, password);
    if (isValid) {
      sessionStorage.setItem('isAuthenticated', 'true');
      redirectToDashboard();
    } else {
      showError('Invalid username or password.');
    }
  } catch (error) {
    showError('Authentication service is unavailable. Please try again.');
  }
});
