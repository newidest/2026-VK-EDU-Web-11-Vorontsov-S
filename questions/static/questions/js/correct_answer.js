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
        const badge = document.querySelector(`span[data-correct-badge="${item.dataset.correctAnswerId}"]`);

        const request = new Request(
            item.dataset.url,
            {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
                mode: 'same-origin'
            }
        );

        fetch(request).then(function(response) {
            if (!response.ok) return;
            response.json().then((data) => {
                if (badge) {
                    badge.hidden = !data.is_correct;
                }
                item.classList.toggle('active-btn', data.is_correct);
            });
        });
    });
}