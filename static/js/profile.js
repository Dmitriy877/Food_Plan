document.getElementById('change-username').addEventListener('click', function(e) {
    e.preventDefault();
    const usernameField = document.getElementById('id_username');
    usernameField.readOnly = !usernameField.readOnly;

    if (!usernameField.readOnly) {
        usernameField.focus();
        usernameField.select();
    }
});

document.getElementById('change-password').addEventListener('click', function(e) {
    e.preventDefault();
    const passwordField1 = document.getElementById('id_new_password1');
    const passwordField2 = document.getElementById('id_new_password2');
    passwordField1.readOnly = !passwordField1.readOnly;
    passwordField2.readOnly = !passwordField2.readOnly;

    if (!passwordField1.readOnly) {
        passwordField1.focus();
    }
});

document.getElementById('avatar-upload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        if (!file.type.match('image.*')) {
            alert('Пожалуйста, выберите файл изображения.');
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            alert('Размер файла не должен превышать 5MB.');
            return;
        }
        uploadAvatar(file);
    }
});

function uploadAvatar(file) {
    const formData = new FormData();
    formData.append('avatar', file);
    formData.append('csrfmiddlewaretoken', document.getElementById('csrf_token').value);

    const avatarImage = document.getElementById('avatar-image');
    const originalSrc = avatarImage.src;
    avatarImage.style.opacity = '0.5';

    fetch('/profile/upload-avatar/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            avatarImage.src = data.avatar_url + '?t=' + new Date().getTime(); // Добавляем timestamp для избежания кэширования
            showMessage('Аватар успешно обновлен!', 'success');
        } else {
            throw new Error(data.error || 'Ошибка загрузки');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        avatarImage.src = originalSrc;
        showMessage('Ошибка загрузки аватара: ' + error.message, 'danger');
    })
    .finally(() => {
        avatarImage.style.opacity = '1';
        document.getElementById('avatar-upload').value = '';
    });
}

function showMessage(message, type) {
    let messageContainer = document.getElementById('avatar-messages');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'avatar-messages';
        document.querySelector('.container').prepend(messageContainer);
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    messageContainer.appendChild(alertDiv);

    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}