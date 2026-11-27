(function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');
    const correctButtons = document.querySelectorAll('button[data-correct-answer-id]');

    for (const item of correctButtons) {
        item.addEventListener('click', () => {
            const request = new Request(
                item.dataset.url,
                {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Accept': 'application/json',
                    },
                    mode: 'same-origin'
                }
            );

            fetch(request)
                .then((response) => {
                    if (response.status === 401) {
                        response.json().catch(() => ({})).then((data) => {
                            const loginUrl = data.login_url || '/login/';
                            const next = encodeURIComponent(window.location.pathname + window.location.search);
                            window.location.href = `${loginUrl}?next=${next}`;
                        });
                        return;
                    }

                    if (!response.ok) {
                        response.json().catch(() => ({})).then((data) => {
                            alert(data.error || `Ошибка запроса (${response.status})`);
                        });
                        return;
                    }

                    response.json().then((data) => {
                        const targetId = String(data.answer_id || item.dataset.correctAnswerId);

                        for (const btn of correctButtons) {
                            const isTarget = btn.dataset.correctAnswerId === targetId;
                            btn.classList.toggle('active-btn', isTarget && data.is_correct);
                        }

                        const badges = document.querySelectorAll('span[data-correct-badge]');
                        for (const badge of badges) {
                            const isTarget = badge.dataset.correctBadge === targetId;
                            badge.hidden = !(isTarget && data.is_correct);
                        }
                    });
                })
                .catch(() => {
                    alert('Ошибка сети. Проверьте подключение.');
                });
        });
    }
})();