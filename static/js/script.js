document.addEventListener('DOMContentLoaded', function() {
    const authPages = ['/login/', '/signup/', '/forgot-password/', '/reset-password/'];
    const currentPath = window.location.pathname;

    if (isAuthenticated()) {
        document.getElementById('navbar').style.display = 'block';
        const isAuthPage = authPages.includes(currentPath) ||
            currentPath === '/verify/' ||
            currentPath === '/complete-profile/' ||
            currentPath === '/upload-photo/';
        if (isAuthPage && currentPath !== '/') {
            checkAuthStatus();
        }
    } else {
        document.getElementById('navbar').style.display = 'none';
        if (!authPages.includes(currentPath) && currentPath !== '/signup/' && currentPath !== '/' &&
            !currentPath.startsWith('/post/') && currentPath !== '/verify/') {
            if (currentPath !== '/') {
                window.location.href = '/login/';
            }
        }
    }

    if (currentPath === '/' && !isAuthenticated()) {
        window.location.href = '/login/';
    }
});

async function checkAuthStatus() {
    try {
        const res = await apiRequest('/users/login/refresh/', {
            method: 'POST',
            body: JSON.stringify({ refresh: getRefreshToken() })
        });
        if (!res.ok) {
            clearTokens();
            window.location.href = '/login/';
        }
    } catch {
        clearTokens();
        window.location.href = '/login/';
    }
}

function showError(elementId, message) {
    const el = document.getElementById(elementId);
    el.textContent = message;
    el.style.display = 'block';
}

function hideError(elementId) {
    const el = document.getElementById(elementId);
    el.textContent = '';
    el.style.display = 'none';
}

function showSuccess(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) { el.textContent = message; el.style.display = 'block'; }
}

function hideSuccess(elementId) {
    const el = document.getElementById(elementId);
    if (el) { el.textContent = ''; el.style.display = 'none'; }
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

function getImageUrl(path) {
    if (!path) return '';
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    return `/media/${path}`;
}

function getUserIdFromToken() {
    try {
        const token = getAccessToken();
        if (!token) return null;
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.user_id;
    } catch { return null; }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (mins < 1) return 'hozir';
    if (mins < 60) return mins + ' min oldin';
    if (hours < 24) return hours + ' soat oldin';
    if (days < 7) return days + ' kun oldin';
    return date.toLocaleDateString('uz-UZ');
}

// ==================== AUTH ====================

async function handleLogin(e) {
    e.preventDefault();
    hideError('loginError');
    const btn = document.getElementById('loginBtn');
    btn.disabled = true;
    btn.textContent = 'Kirish...';

    try {
        const res = await apiRequest('/users/login/', {
            method: 'POST',
            body: JSON.stringify({
                user_input: document.getElementById('user_input').value,
                password: document.getElementById('password').value
            })
        });
        const data = await res.json();
        if (!res.ok) {
            showError('loginError', data.detail || 'Xatolik yuz berdi');
            btn.disabled = false;
            btn.textContent = 'Kirish';
            return;
        }
        setTokens(data.access, data.refresh);
        window.location.href = data.is_staff ? '/admin/' : '/';
    } catch (err) {
        showError('loginError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Kirish';
    }
}

async function handleSignup(e) {
    e.preventDefault();
    hideError('signupError');
    const btn = document.getElementById('signupBtn');
    btn.disabled = true;
    btn.textContent = 'Yuborilmoqda...';

    try {
        const res = await apiRequest('/users/signup/', {
            method: 'POST',
            body: JSON.stringify({
                email_phone_number: document.getElementById('email_phone').value
            })
        });
        const data = await res.json();
        if (!res.ok) {
            showError('signupError', data.email_phone_number?.[0] || data.error || 'Xatolik yuz berdi');
            btn.disabled = false;
            btn.textContent = 'Ro\'yxatdan o\'tish';
            return;
        }
        setTokens(data.access, data.refresh_token);
        window.location.href = '/verify/';
    } catch (err) {
        showError('signupError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Ro\'yxatdan o\'tish';
    }
}

async function handleVerify(e) {
    e.preventDefault();
    hideError('verifyError');
    const btn = document.getElementById('verifyBtn');
    btn.disabled = true;
    btn.textContent = 'Tekshirilmoqda...';

    try {
        const res = await apiRequest('/users/verify/', {
            method: 'POST',
            body: JSON.stringify({
                code: document.getElementById('verify_code').value
            })
        });
        const data = await res.json();
        if (!res.ok) {
            showError('verifyError', data.error || data.code?.[0] || 'Xato kod');
            btn.disabled = false;
            btn.textContent = 'Tasdiqlash';
            return;
        }
        window.location.href = '/complete-profile/';
    } catch (err) {
        showError('verifyError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Tasdiqlash';
    }
}

async function resendCode() {
    const btn = document.getElementById('resendBtn');
    btn.disabled = true;
    btn.textContent = 'Yuborilmoqda...';

    try {
        const res = await apiRequest('/users/new-verify/', { method: 'GET' });
        if (res.ok) {
            alert('Yangi kod yuborildi');
        } else {
            alert('Xatolik yuz berdi');
        }
    } catch {
        alert('Server bilan bog\'lanishda xatolik');
    }
    btn.disabled = false;
    btn.textContent = 'Kodni qayta yuborish';
}

async function handleCompleteProfile(e) {
    e.preventDefault();
    hideError('profileError');
    const btn = document.getElementById('profileBtn');
    btn.disabled = true;
    btn.textContent = 'Saqlanmoqda...';

    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm_password').value;

    if (password !== confirm) {
        showError('profileError', 'Parollar mos kelmadi');
        btn.disabled = false;
        btn.textContent = 'Saqlash';
        return;
    }

    try {
        const res = await apiRequest('/users/change-user/', {
            method: 'PATCH',
            body: JSON.stringify({
                first_name: document.getElementById('first_name').value,
                last_name: document.getElementById('last_name').value,
                username: document.getElementById('username').value,
                password: password,
                confirm_password: confirm
            })
        });
        if (!res.ok) {
            const data = await res.json();
            const errors = [];
            if (data.first_name) errors.push(data.first_name[0]);
            if (data.last_name) errors.push(data.last_name[0]);
            if (data.username) errors.push(data.username[0]);
            if (data.password) errors.push(data.password[0]);
            if (data.non_field_errors) errors.push(data.non_field_errors[0]);
            showError('profileError', errors.join('. ') || 'Xatolik yuz berdi');
            btn.disabled = false;
            btn.textContent = 'Saqlash';
            return;
        }
        window.location.href = '/upload-photo/';
    } catch (err) {
        showError('profileError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Saqlash';
    }
}

async function handleUploadPhoto(e) {
    e.preventDefault();
    hideError('photoError');
    const btn = document.getElementById('photoBtn');
    btn.disabled = true;
    btn.textContent = 'Yuklanmoqda...';

    const fileInput = document.getElementById('photo');
    if (!fileInput.files.length) {
        showError('photoError', 'Rasm tanlang');
        btn.disabled = false;
        btn.textContent = 'Yuklash';
        return;
    }

    const formData = new FormData();
    formData.append('photo', fileInput.files[0]);

    try {
        const res = await apiRequest('/users/change-photo-user/', {
            method: 'PUT',
            body: formData
        });
        if (!res.ok) {
            const data = await res.json();
            showError('photoError', data.photo?.[0] || data.error || 'Xatolik yuz berdi');
            btn.disabled = false;
            btn.textContent = 'Yuklash';
            return;
        }
        window.location.href = '/';
    } catch (err) {
        showError('photoError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Yuklash';
    }
}

async function handleForgotPassword(e) {
    e.preventDefault();
    hideError('forgotError');
    const btn = document.getElementById('forgotBtn');
    btn.disabled = true;
    btn.textContent = 'Yuborilmoqda...';

    try {
        const res = await apiRequest('/users/forgot-password/', {
            method: 'POST',
            body: JSON.stringify({
                email_or_phone: document.getElementById('email_or_phone').value
            })
        });
        const data = await res.json();
        if (!res.ok) {
            showError('forgotError', data.error || data.email_or_phone?.[0] || 'Xatolik yuz berdi');
            btn.disabled = false;
            btn.textContent = 'Kod yuborish';
            return;
        }
        setTokens(data.access, data.refresh || data.refresh_token);
        window.location.href = '/reset-password/';
    } catch (err) {
        showError('forgotError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Kod yuborish';
    }
}

async function handleResetPassword(e) {
    e.preventDefault();
    hideError('resetError');
    const btn = document.getElementById('resetBtn');
    btn.disabled = true;
    btn.textContent = 'Saqlanmoqda...';

    const password = document.getElementById('new_password').value;
    const confirm = document.getElementById('confirm_password').value;

    if (password !== confirm) {
        showError('resetError', 'Parollar mos kelmadi');
        btn.disabled = false;
        btn.textContent = 'Saqlash';
        return;
    }

    try {
        const res = await apiRequest('/users/reset-password/', {
            method: 'PATCH',
            body: JSON.stringify({
                password: password,
                confirm_password: confirm
            })
        });
        if (!res.ok) {
            const data = await res.json();
            showError('resetError', data.password?.[0] || data.error || 'Xatolik yuz berdi');
            btn.disabled = false;
            btn.textContent = 'Saqlash';
            return;
        }
        clearTokens();
        alert('Parol muvaffaqiyatli o\'zgartirildi! Iltimos, qaytadan kiring.');
        window.location.href = '/login/';
    } catch (err) {
        showError('resetError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Saqlash';
    }
}

function logoutUser() {
    const refresh = getRefreshToken();
    if (refresh) {
        apiRequest('/users/logout/', {
            method: 'POST',
            body: JSON.stringify({ refresh })
        }).catch(() => {});
    }
    clearTokens();
    window.location.href = '/login/';
}

// ==================== PHOTO PREVIEW ====================

document.addEventListener('change', function(e) {
    if (e.target.type === 'file' && e.target.files.length) {
        const preview = e.target.closest('.form-group')?.querySelector('.photo-preview, .post-upload-preview');
        if (preview) {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = function(ev) {
                if (file.type.startsWith('video/')) {
                    preview.innerHTML = `<video src="${ev.target.result}" controls style="width:100%;max-height:400px;object-fit:contain;"></video>`;
                } else {
                    preview.innerHTML = `<img src="${ev.target.result}" alt="Preview">`;
                }
            };
            reader.readAsDataURL(file);
        }
    }
});

document.addEventListener('click', function(e) {
    const preview = e.target.closest('.post-upload-preview');
    if (preview) {
        const fileInput = preview.closest('.form-group')?.querySelector('.form-input-file');
        if (fileInput) fileInput.click();
    }
});

// ==================== FEED ====================

let currentPage = 1;
let totalPages = 1;

async function loadFeed(page = 1) {
    const container = document.getElementById('postList');
    if (!container) return;
    container.innerHTML = '<div class="loading">Yuklanmoqda...</div>';

    const url = isAuthenticated() ? `/post/feed/?page=${page}` : `/post/list/?page=${page}`;

    try {
        const res = await apiRequest(url);
        if (!res.ok) {
            container.innerHTML = '<div class="empty-state"><p>Xatolik yuz berdi</p></div>';
            return;
        }
        const data = await res.json();
        const posts = data.result || data.results || data;
        currentPage = page;
        totalPages = Math.ceil((data.count || 0) / 10);

        showFeedHeader();
        if (!posts.length) {
            container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📷</div><h3>Hozircha postlar yo\'q</h3><p>Birinchi bo\'lib post yarating va<br>do\'stlaringiz bilan ulashing!</p><a href="/post/new/" class="btn btn-primary">Post yaratish</a></div>';
            renderPagination(data);
            return;
        }

        container.innerHTML = '';
        for (const post of posts) {
            container.appendChild(createPostCard(post));
        }
        renderPagination(data);
    } catch (err) {
        container.innerHTML = '<div class="empty-state"><p>Xatolik yuz berdi</p></div>';
    }
}

function showFeedHeader() {
    const header = document.getElementById('feedHeader');
    if (!header) return;
    const avatarEl = document.getElementById('feedUserAvatar');
    const nameEl = document.getElementById('feedUsername');
    const userId = getUserIdFromToken();
    if (!userId) return;
    header.style.display = 'block';
    apiRequest(`/users/${userId}/`).then(res => {
        if (!res.ok) return;
        res.json().then(data => {
            const user = data.user || {};
            const photo = getImageUrl(user.photo);
            if (avatarEl) {
                avatarEl.innerHTML = photo ? `<img src="${photo}" alt="avatar">` : '';
            }
            if (nameEl) nameEl.textContent = user.username || '';
        });
    }).catch(() => {});
}

function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';

    const authorPhoto = getImageUrl(post.author?.photo);
    const imageUrl = getImageUrl(post.image);
    const videoUrl = post.video ? getImageUrl(post.video) : null;

    const profileLink = post.author?.id ? `/profile/${post.author.id}/` : '/profile/';

    let mediaHtml = '';
    if (videoUrl) {
        mediaHtml = `<video src="${videoUrl}" class="post-image" loop muted playsinline preload="metadata"></video>`;
    } else if (imageUrl) {
        mediaHtml = `<img src="${imageUrl}" alt="Post" class="post-image" loading="lazy">`;
    }

    card.innerHTML = `
        <div class="post-header">
            <div class="post-avatar" onclick="window.location.href='${profileLink}'">
                <div class="post-avatar-inner">
                    ${authorPhoto ? `<img src="${authorPhoto}" alt="avatar">` : ''}
                </div>
            </div>
            <a href="${profileLink}" class="post-username">${escapeHtml(post.author?.username || 'noma\'lum')}</a>
        </div>
        ${mediaHtml}
        <div class="post-actions">
            <button class="post-action-btn ${post.liked_me ? 'liked' : ''}" onclick="toggleLike('${post.id}', this)">
                ${post.liked_me ? '❤️' : '🤍'}
            </button>
            <button class="post-action-btn" onclick="window.location.href='/post/${post.id}/'">
                💬
            </button>
        </div>
        <div class="post-likes">${post.post_like_count || 0} ta like</div>
        <div class="post-caption">
            <strong>${escapeHtml(post.author?.username || 'noma\'lum')}</strong>
            ${escapeHtml(post.caption || '')}
        </div>
        <div class="post-comments-link" onclick="window.location.href='/post/${post.id}/'">
            ${post.post_comment_count || 0} ta izoh
        </div>
        <div class="post-time">${formatDate(post.created_time)}</div>
    `;
    return card;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderPagination(data) {
    const container = document.getElementById('pagination');
    if (!container) return;
    if (!data.count || data.count <= 10) {
        container.innerHTML = '';
        return;
    }

    container.innerHTML = '';
    if (data.previous) {
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '← Oldingi';
        prevBtn.onclick = () => loadFeed(currentPage - 1);
        container.appendChild(prevBtn);
    }

    const total = Math.ceil(data.count / 10);
    for (let i = 1; i <= total; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.className = i === currentPage ? 'active' : '';
        btn.onclick = () => loadFeed(i);
        container.appendChild(btn);
    }

    if (data.next) {
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Keyingi →';
        nextBtn.onclick = () => loadFeed(currentPage + 1);
        container.appendChild(nextBtn);
    }
}

// ==================== LIKE ====================

async function toggleLike(postId, btn) {
    try {
        const res = await apiRequest(`/post/${postId}/create-delete-like/`, {
            method: 'POST'
        });
        if (res.ok) {
            const isLiked = btn.classList.toggle('liked');
            btn.textContent = isLiked ? '❤️' : '🤍';
            const likesEl = btn.closest('.post-card')?.querySelector('.post-likes');
            if (likesEl) {
                let count = parseInt(likesEl.textContent) || 0;
                likesEl.textContent = `${isLiked ? count + 1 : Math.max(0, count - 1)} ta like`;
            }
        }
    } catch (err) {
        console.error('Like error:', err);
    }
}

// ==================== POST DETAIL ====================

async function loadPostDetail() {
    const container = document.getElementById('postDetail');
    const detailPage = document.querySelector('.post-detail-page');
    if (!container || !detailPage) return;

    const postId = detailPage.dataset.postId;
    if (!postId) return;

    try {
        const res = await apiRequest(`/post/${postId}/`);
        if (!res.ok) {
            container.innerHTML = '<div class="empty-state"><p>Post topilmadi</p></div>';
            return;
        }
        const post = await res.json();

        const authorPhoto = getImageUrl(post.author?.photo);
        const imageUrl = getImageUrl(post.image);
        const videoUrl = post.video ? getImageUrl(post.video) : null;

        let mediaHtml = '';
        if (videoUrl) {
            mediaHtml = `<video src="${videoUrl}" controls class="post-detail-image"></video>`;
        } else if (imageUrl) {
            mediaHtml = `<img src="${imageUrl}" alt="Post" class="post-detail-image">`;
        }

        container.innerHTML = `
            <div class="post-card">
                <div class="post-header">
                    <div class="post-avatar" onclick="window.location.href='/profile/${post.author?.id || ''}/'">
                        <div class="post-avatar-inner">
                            ${authorPhoto ? `<img src="${authorPhoto}" alt="avatar">` : ''}
                        </div>
                    </div>
                    <a href="/profile/${post.author?.id || ''}/" class="post-username">${escapeHtml(post.author?.username || 'noma\'lum')}</a>
                </div>
                ${mediaHtml}
                <div class="post-actions">
                    <button class="post-action-btn ${post.liked_me ? 'liked' : ''}" onclick="toggleLike('${post.id}', this)">
                        ${post.liked_me ? '❤️' : '🤍'}
                    </button>
                    <button class="post-action-btn" onclick="document.getElementById('comment_text').focus()">
                        💬
                    </button>
                </div>
                <div class="post-likes" id="detailLikes">${post.post_like_count || 0} ta like</div>
                <div class="post-caption">
                    <strong>${escapeHtml(post.author?.username || 'noma\'lum')}</strong>
                    ${escapeHtml(post.caption || '')}
                </div>
                <div class="post-time">${formatDate(post.created_time)}</div>
            </div>
        `;
    } catch (err) {
        container.innerHTML = '<div class="empty-state"><p>Xatolik yuz berdi</p></div>';
    }
}

// ==================== COMMENTS ====================

async function loadComments(postId) {
    const container = document.getElementById('commentsList');
    if (!container) return;

    try {
        const res = await apiRequest(`/post/${postId}/comments/`);
        if (!res.ok) {
            container.innerHTML = '<div class="empty-state"><p>Izohlar yuklanmadi</p></div>';
            return;
        }
        const data = await res.json();
        const comments = data.result || data.results || data;

        if (!comments.length) {
            container.innerHTML = '<div class="empty-state"><p>Hozircha izohlar yo\'q</p></div>';
            return;
        }

        container.innerHTML = '';
        for (const comment of comments) {
            container.appendChild(createCommentElement(comment));
        }
    } catch (err) {
        container.innerHTML = '<div class="empty-state"><p>Xatolik yuz berdi</p></div>';
    }
}

function createCommentElement(comment) {
    const div = document.createElement('div');
    div.className = 'comment-item';
    div.id = `comment-${comment.id}`;

    const authorPhoto = getImageUrl(comment.author?.photo);

    div.innerHTML = `
        <div class="comment-header">
            <div class="post-avatar">
                <div class="post-avatar-inner">
                    ${authorPhoto ? `<img src="${authorPhoto}" alt="avatar">` : ''}
                </div>
            </div>
            <a href="/profile/" class="comment-author">${escapeHtml(comment.author?.username || 'noma\'lum')}</a>
            <span class="comment-time">${formatDate(comment.created_time)}</span>
        </div>
        <div class="comment-text">${escapeHtml(comment.comment)}</div>
        <div class="comment-actions">
            <button class="comment-like-btn ${comment.liked_me ? 'liked' : ''}" onclick="toggleCommentLike('${comment.id}', this)">
                ${comment.liked_me ? '❤️' : '🤍'}
            </button>
            <span class="comment-likes-count">${comment.like_count || 0}</span>
        </div>
        ${comment.replies && comment.replies.length ? createRepliesHtml(comment.replies) : ''}
    `;
    return div;
}

function createRepliesHtml(replies) {
    let html = '<div class="replies">';
    for (const reply of replies) {
        const replyPhoto = getImageUrl(reply.author?.photo);
        html += `
            <div class="reply-item">
                <div class="comment-header">
                    <div class="post-avatar" style="width:24px;height:24px;">
                        <div class="post-avatar-inner">
                            ${replyPhoto ? `<img src="${replyPhoto}" alt="avatar">` : ''}
                        </div>
                    </div>
                    <span class="comment-author">${escapeHtml(reply.author?.username || 'noma\'lum')}</span>
                    <span class="comment-time">${formatDate(reply.created_time)}</span>
                </div>
                <div class="comment-text">${escapeHtml(reply.comment)}</div>
                <div class="comment-actions">
                    <button class="comment-like-btn ${reply.liked_me ? 'liked' : ''}" onclick="toggleCommentLike('${reply.id}', this)">
                        ${reply.liked_me ? '❤️' : '🤍'}
                    </button>
                    <span class="comment-likes-count">${reply.like_count || 0}</span>
                </div>
            </div>
        `;
    }
    html += '</div>';
    return html;
}

async function handleCreateComment(e, postId) {
    e.preventDefault();
    const input = document.getElementById('comment_text');
    const text = input.value.trim();
    if (!text) return;

    try {
        const res = await apiRequest(`/post/${postId}/comments/create/`, {
            method: 'POST',
            body: JSON.stringify({
                post: postId,
                comment: text
            })
        });
        if (res.ok) {
            input.value = '';
            loadComments(postId);
        } else {
            const data = await res.json();
            alert(data.comment?.[0] || data.error || 'Xatolik yuz berdi');
        }
    } catch (err) {
        alert('Server bilan bog\'lanishda xatolik');
    }
}

async function toggleCommentLike(commentId, btn) {
    try {
        const res = await apiRequest(`/post/${commentId}/comment-like_delete/`, {
            method: 'POST'
        });
        if (res.ok) {
            const isLiked = btn.classList.toggle('liked');
            btn.textContent = isLiked ? '❤️' : '🤍';
            const countEl = btn.nextElementSibling;
            if (countEl) {
                let count = parseInt(countEl.textContent) || 0;
                countEl.textContent = isLiked ? count + 1 : Math.max(0, count - 1);
            }
        }
    } catch (err) {
        console.error('Comment like error:', err);
    }
}

// ==================== CREATE POST ====================

async function handleCreatePost(e) {
    e.preventDefault();
    hideError('postError');
    const btn = document.getElementById('createPostBtn');
    btn.disabled = true;
    btn.textContent = 'Yuborilmoqda...';

    const fileInput = document.getElementById('post_image');
    if (!fileInput.files.length) {
        showError('postError', 'Rasm yoki video tanlang');
        btn.disabled = false;
        btn.textContent = 'Post qilish';
        return;
    }

    const formData = new FormData();
    const file = fileInput.files[0];
    const isVideo = file.type.startsWith('video/');
    if (isVideo) {
        formData.append('video', file);
    } else {
        formData.append('image', file);
    }
    const caption = document.getElementById('caption').value.trim();
    if (caption) {
        formData.append('caption', caption);
    }

    try {
        const res = await apiRequest('/post/create/', {
            method: 'POST',
            body: formData
        });
        if (!res.ok) {
            const data = await res.json();
            const errMsg = data.image?.[0] || data.video?.[0] || data.caption?.[0] || data.media?.[0] || data.error || 'Xatolik yuz berdi';
            showError('postError', errMsg);
            btn.disabled = false;
            btn.textContent = 'Post qilish';
            return;
        }
        const post = await res.json();
        window.location.href = `/post/${post.id}/`;
    } catch (err) {
        showError('postError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Post qilish';
    }
}

// ==================== PROFILE ====================

async function loadProfile() {
    const infoContainer = document.getElementById('profileInfo');
    if (!infoContainer) return;

    const userId = getUserIdFromToken();
    if (!userId) {
        infoContainer.innerHTML = '<div class="empty-state"><p>Avval tizimga kiring</p></div>';
        return;
    }

    try {
        const [userRes, postsRes] = await Promise.all([
            apiRequest(`/users/${userId}/`),
            apiRequest(`/post/list/?page=1&page_size=100`)
        ]);

        const userData = userRes.ok ? await userRes.json() : null;
        const user = userData?.user || {};
        const postsData = postsRes.ok ? await postsRes.json() : {};
        const allPosts = postsData.result || postsData.results || postsData;

        const myPosts = Array.isArray(allPosts) ? allPosts.filter(p => p.author?.id === userId) : [];
        const username = user.username || 'foydalanuvchi';
        const userPhoto = getImageUrl(user.photo);
        const followerCount = user.follower_count ?? 0;
        const followingCount = user.following_count ?? 0;

        infoContainer.innerHTML = `
            <div class="profile-avatar">
                <div class="profile-avatar-inner">
                    ${userPhoto ? `<img src="${userPhoto}" alt="Profile photo">` : ''}
                </div>
            </div>
            <div class="profile-details">
                <h2 class="profile-username">${escapeHtml(username)}</h2>
                <p class="profile-fullname">${escapeHtml(user.full_name || username)}</p>
                <div class="profile-stats">
                    <span class="profile-stat"><strong>${myPosts.length}</strong> post</span>
                    <span class="profile-stat" style="cursor:pointer;" onclick="window.location.href='/profile/${userId}/followers/'"><strong>${followerCount}</strong> obunachilar</span>
                    <span class="profile-stat" style="cursor:pointer;" onclick="window.location.href='/profile/${userId}/following/'"><strong>${followingCount}</strong> obuna</span>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;">
                    <a href="/upload-photo/" class="profile-edit-btn">Rasmni o'zgartirish</a>
                    <a href="/settings/" class="profile-edit-btn">Sozlamalar</a>
                </div>
            </div>
        `;

        const myPostsContainer = document.getElementById('myPosts');
        if (!myPostsContainer) return;

        if (!myPosts.length) {
            myPostsContainer.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📷</div><h3>Postlar yo\'q</h3><p>Siz hali post yaratmadingiz</p><a href="/post/new/" class="btn btn-primary">Post yaratish</a></div>';
            return;
        }

        myPostsContainer.innerHTML = '';
        for (const post of myPosts) {
            const item = document.createElement('div');
            item.className = 'profile-post-item';
            const imgUrl = getImageUrl(post.image);
            item.innerHTML = `
                ${imgUrl ? `<img src="${imgUrl}" alt="Post" class="profile-post-img">` : `<div class="profile-post-img"></div>`}
                <div class="profile-post-info">
                    <div class="profile-post-caption">${escapeHtml(post.caption || 'Sarlavhasiz')}</div>
                    <div class="profile-post-date">${formatDate(post.created_time)} · ${post.post_like_count || 0} ta like</div>
                </div>
                <a href="/post/${post.id}/" class="btn btn-sm btn-outline">Ko\'rish</a>
            `;
            myPostsContainer.appendChild(item);
        }
    } catch (err) {
        infoContainer.innerHTML = '<div class="empty-state"><p>Xatolik yuz berdi</p></div>';
    }
}

// ==================== SEARCH ====================

let searchTimeout = null;

async function searchUsers(query) {
    clearTimeout(searchTimeout);
    const results = document.getElementById('searchResults');
    if (!results) return;

    if (!query.trim()) {
        results.innerHTML = '<div class="empty-state" style="border:none;padding:40px 0;"><p>Qidirish uchun matn yozing</p></div>';
        return;
    }

    searchTimeout = setTimeout(async () => {
        results.innerHTML = '<div class="loading" style="padding:20px;">Qidirilmoqda...</div>';
        try {
            const res = await apiRequest(`/users/search/?q=${encodeURIComponent(query)}`);
            if (!res.ok) {
                results.innerHTML = '<div class="empty-state" style="border:none;padding:40px 0;"><p>Xatolik yuz berdi</p></div>';
                return;
            }
            const data = await res.json();
            if (!data.length) {
                results.innerHTML = '<div class="empty-state" style="border:none;padding:40px 0;"><p>Hech narsa topilmadi</p></div>';
                return;
            }
            results.innerHTML = '';
            for (const user of data) {
                const item = document.createElement('a');
                item.href = `/profile/${user.id}/`;
                item.className = 'search-user-item';
                const userPhoto = getImageUrl(user.photo);
                item.innerHTML = `
                    <div class="search-user-avatar">
                        <div class="search-user-avatar-inner">
                            ${userPhoto ? `<img src="${userPhoto}" alt="avatar">` : ''}
                        </div>
                    </div>
                    <div class="search-user-info">
                        <div class="search-user-username">${escapeHtml(user.username)}</div>
                        <div class="search-user-name">${escapeHtml(user.full_name || '')}</div>
                        <div class="search-user-stats">${user.post_count} post · ${user.follower_count} followers</div>
                    </div>
                `;
                results.appendChild(item);
            }
        } catch (err) {
            results.innerHTML = '<div class="empty-state" style="border:none;padding:40px 0;"><p>Xatolik yuz berdi</p></div>';
        }
    }, 400);
}

// ==================== USER PROFILE (OTHER USERS) ====================

async function loadUserProfile() {
    const container = document.getElementById('userProfileInfo');
    if (!container) return;

    const userId = document.querySelector('.profile-page')?.dataset?.userId;
    if (!userId) return;

    try {
        const res = await apiRequest(`/users/${userId}/`);
        if (!res.ok) {
            container.innerHTML = '<div class="empty-state"><p>Foydalanuvchi topilmadi</p></div>';
            return;
        }
        const data = await res.json();
        const user = data.user;
        const posts = data.posts || [];
        const userPhoto = getImageUrl(user.photo);
        const currentUserId = getUserIdFromToken();

        container.innerHTML = `
            <div class="profile-avatar">
                <div class="profile-avatar-inner">
                    ${userPhoto ? `<img src="${userPhoto}" alt="Profile photo">` : ''}
                </div>
            </div>
            <div class="profile-details">
                <h2 class="profile-username">${escapeHtml(user.username)}</h2>
                <p class="profile-fullname">${escapeHtml(user.full_name || '')}</p>
                <div class="profile-stats">
                    <span class="profile-stat"><strong>${user.post_count}</strong> post</span>
                    <span class="profile-stat" style="cursor:pointer;" onclick="window.location.href='/profile/${userId}/followers/'"><strong>${user.follower_count}</strong> obunachilar</span>
                    <span class="profile-stat" style="cursor:pointer;" onclick="window.location.href='/profile/${userId}/following/'"><strong>${user.following_count}</strong> obuna</span>
                </div>
                ${currentUserId && currentUserId !== userId ? `
                    <button class="follow-btn ${data.is_following ? 'follow-btn-following' : 'follow-btn-follow'}" 
                            onclick="toggleFollow('${userId}', this)">
                        ${data.is_following ? 'Kuzatilmoqda' : 'Kuzatish'}
                    </button>
                ` : ''}
                ${currentUserId === userId ? '<a href="/upload-photo/" class="profile-edit-btn">Rasmni o\'zgartirish</a>' : ''}
            </div>
        `;

        const postsContainer = document.getElementById('userPosts');
        if (!postsContainer) return;

        if (!posts.length) {
            postsContainer.innerHTML = '<div class="empty-state" style="border:none;"><p>Postlar yo\'q</p></div>';
            return;
        }

        postsContainer.innerHTML = '';
        for (const post of posts) {
            const item = document.createElement('div');
            item.className = 'profile-post-item';
            const imgUrl = getImageUrl(post.image);
            item.innerHTML = `
                ${imgUrl ? `<img src="${imgUrl}" alt="Post" class="profile-post-img">` : `<div class="profile-post-img"></div>`}
                <div class="profile-post-info">
                    <div class="profile-post-caption">${escapeHtml(post.caption || 'Sarlavhasiz')}</div>
                    <div class="profile-post-date">${formatDate(post.created_time)} · ${post.post_like_count || 0} ta like</div>
                </div>
                <a href="/post/${post.id}/" class="btn btn-sm btn-outline">Ko\'rish</a>
            `;
            postsContainer.appendChild(item);
        }
    } catch (err) {
        container.innerHTML = '<div class="empty-state"><p>Xatolik yuz berdi</p></div>';
    }
}

// ==================== FOLLOWERS / FOLLOWING LIST ====================

async function loadFollowList() {
    const container = document.getElementById('followList');
    if (!container) return;

    const pathParts = window.location.pathname.split('/').filter(Boolean);
    if (pathParts.length < 3) return;
    const userId = pathParts[1];
    const listType = pathParts[2];
    const titleEl = document.getElementById('followListTitle');
    if (titleEl) {
        titleEl.textContent = listType === 'following' ? 'Obunalar' : 'Obunachilar';
    }

    try {
        const res = await apiRequest(`/users/${userId}/${listType}/`);
        if (!res.ok) {
            container.innerHTML = '<div class="empty-state" style="border:none;padding:20px 0;"><p>Xatolik yuz berdi</p></div>';
            return;
        }
        const users = await res.json();
        if (!users.length) {
            container.innerHTML = '<div class="empty-state" style="border:none;padding:20px 0;"><p>Hech kim yo\'q</p></div>';
            return;
        }

        container.innerHTML = '';
        for (const u of users) {
            const item = document.createElement('a');
            item.href = `/profile/${u.id}/`;
            item.className = 'search-user-item';
            const userPhoto = getImageUrl(u.photo);
            item.innerHTML = `
                <div class="search-user-avatar">
                    <div class="search-user-avatar-inner">
                        ${userPhoto ? `<img src="${userPhoto}" alt="avatar">` : ''}
                    </div>
                </div>
                <div class="search-user-info">
                    <div class="search-user-username">${escapeHtml(u.username)}</div>
                    <div class="search-user-name">${escapeHtml(u.full_name || '')}</div>
                </div>
            `;
            container.appendChild(item);
        }
    } catch (err) {
        container.innerHTML = '<div class="empty-state" style="border:none;padding:20px 0;"><p>Xatolik yuz berdi</p></div>';
    }
}

async function toggleFollow(userId, btn) {
    try {
        const res = await apiRequest(`/users/${userId}/follow/`, {
            method: 'POST'
        });
        if (res.ok) {
            const data = await res.json();
            if (data.following) {
                btn.textContent = 'Kuzatilmoqda';
                btn.className = 'follow-btn follow-btn-following';
            } else {
                btn.textContent = 'Kuzatish';
                btn.className = 'follow-btn follow-btn-follow';
            }
            loadUserProfile();
        }
    } catch (err) {
        console.error('Follow error:', err);
    }
}

// ==================== REELS / EXPLORE ====================

let explorePage = 1;

async function loadExplore(page = 1) {
    const container = document.getElementById('exploreGrid');
    if (!container) return;
    container.innerHTML = '<div class="loading">Yuklanmoqda...</div>';

    try {
        const res = await apiRequest(`/post/popular/?page=${page}&page_size=30`);
        if (!res.ok) {
            container.innerHTML = '<div class="empty-state" style="border:none;"><p>Xatolik yuz berdi</p></div>';
            return;
        }
        const data = await res.json();
        const posts = data.result || data.results || data;
        explorePage = page;
        const totalPages = Math.ceil((data.count || 0) / 30);

        if (!posts.length) {
            container.innerHTML = '<div class="empty-state" style="border:none;"><div class="empty-state-icon">📷</div><h3>Hozircha postlar yo\'q</h3></div>';
            renderExplorePagination(data);
            return;
        }

        container.innerHTML = '';
        for (const post of posts) {
            const imgUrl = getImageUrl(post.image);
            const videoUrl = post.video ? getImageUrl(post.video) : null;
            if (!imgUrl && !videoUrl) continue;
            const item = document.createElement('a');
            item.href = `/post/${post.id}/`;
            item.className = 'explore-grid-item';
            const thumbnailUrl = imgUrl || videoUrl;
            const isVideo = !!videoUrl;
            item.innerHTML = `
                ${isVideo ? '<div class="explore-video-badge">🎥</div>' : ''}
                <img src="${thumbnailUrl}" alt="Post" loading="lazy">
                <div class="explore-grid-overlay">
                    <span class="explore-overlay-stat">❤️ ${post.post_like_count || 0}</span>
                    <span class="explore-overlay-stat">💬 ${post.post_comment_count || 0}</span>
                </div>
            `;
            container.appendChild(item);
        }
        renderExplorePagination(data);
    } catch (err) {
        container.innerHTML = '<div class="empty-state" style="border:none;"><p>Xatolik yuz berdi</p></div>';
    }
}

function renderExplorePagination(data) {
    const container = document.getElementById('explorePagination');
    if (!container) return;
    if (!data.count || data.count <= 30) {
        container.innerHTML = '';
        return;
    }

    const total = Math.ceil(data.count / 30);
    container.innerHTML = '';

    if (data.previous) {
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '← Oldingi';
        prevBtn.onclick = () => loadExplore(explorePage - 1);
        container.appendChild(prevBtn);
    }

    for (let i = 1; i <= total && i <= 10; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.className = i === explorePage ? 'active' : '';
        btn.onclick = () => loadExplore(i);
        container.appendChild(btn);
    }

    if (data.next) {
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Keyingi →';
        nextBtn.onclick = () => loadExplore(explorePage + 1);
        container.appendChild(nextBtn);
    }
}

// ==================== SETTINGS ====================

async function handleChangeUsername() {
    hideError('changeUsernameError');
    hideSuccess('changeUsernameSuccess');
    const btn = document.getElementById('changeUsernameBtn');
    btn.disabled = true;
    btn.textContent = 'Saqlanmoqda...';

    const body = { current_password: document.getElementById('usernameCurrentPassword').value };
    const newUsername = document.getElementById('newUsername').value;
    if (newUsername) body.username = newUsername;

    try {
        const res = await apiRequest('/users/change-user/', {
            method: 'PATCH',
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok) {
            const msg = data.username?.[0] || data.current_password?.[0] || data.message || 'Xatolik yuz berdi';
            showError('changeUsernameError', msg);
            btn.disabled = false;
            btn.textContent = 'Saqlash';
            return;
        }
        showSuccess('changeUsernameSuccess', 'Username muvaffaqiyatli o\'zgartirildi!');
        btn.disabled = false;
        btn.textContent = 'Saqlash';
    } catch (err) {
        showError('changeUsernameError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Saqlash';
    }
}

async function handleDeleteAccount() {
    if (!confirm('Hisobingizni o\'chirishni xohlaysizmi? Bu amalni qaytarib bo\'lmaydi!')) return;
    hideError('deleteAccountError');
    hideSuccess('deleteAccountSuccess');
    const btn = document.getElementById('deleteAccountBtn');
    btn.disabled = true;
    btn.textContent = 'O\'chirilmoqda...';

    try {
        const res = await apiRequest('/users/delete-account/', {
            method: 'POST',
            body: JSON.stringify({
                password: document.getElementById('deletePassword').value,
                refresh: getRefreshToken()
            })
        });
        const data = await res.json();
        if (!res.ok) {
            const msg = data.password?.[0] || data.message || 'Xatolik yuz berdi';
            showError('deleteAccountError', msg);
            btn.disabled = false;
            btn.textContent = 'Hisobni o\'chirish';
            return;
        }
        showSuccess('deleteAccountSuccess', 'Hisobingiz o\'chirildi. 3 soniyadan keyin chiqib ketasiz...');
        setTimeout(() => { clearTokens(); window.location.href = '/login/'; }, 3000);
    } catch (err) {
        showError('deleteAccountError', 'Server bilan bog\'lanishda xatolik');
        btn.disabled = false;
        btn.textContent = 'Hisobni o\'chirish';
    }
}

// ==================== INIT BY PAGE ====================

const path = window.location.pathname;

if (path === '/' || path === '/post/list/') {
    loadFeed();
} else if (path.startsWith('/post/') && /^\/post\/[0-9a-f-]+\/$/.test(path)) {
    const postId = document.querySelector('.post-detail-page')?.dataset.postId;
    if (postId) {
        loadPostDetail();
        loadComments(postId);
    }
} else if (path === '/explore/' || path === '/reels/') {
    loadExplore();
} else if (path === '/profile/') {
    loadProfile();
} else if (path.startsWith('/profile/') && /^\/profile\/[0-9a-f-]+\/$/.test(path)) {
    loadUserProfile();
} else if (/^\/profile\/[0-9a-f-]+\/(followers|following)\/$/.test(path)) {
    loadFollowList();
}
