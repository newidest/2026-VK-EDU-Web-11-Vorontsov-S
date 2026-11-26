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
    const voteButtons = document.querySelectorAll('button[data-vote-url]');

    for (const btn of voteButtons) {
        btn.addEventListener('click', () => {
            const boxId = btn.dataset.voteBoxId;
            const counter = document.querySelector(`span[data-rating-counter="${boxId}"]`);
            const box = document.querySelector(`[data-vote-box="${boxId}"]`);

            const request = new Request(
                btn.dataset.voteUrl,
                {
                    method: 'POST',
                    headers: {'X-CSRFToken': csrftoken},
                    mode: 'same-origin'
                }
            );

            fetch(request).then(function(response) {
                if (!response.ok) return;
                response.json().then((data) => {
                    if (counter) {
                        counter.innerText = data.rating;
                    }
                    if (box) {
                        const likeBtn = box.querySelector('button[data-vote-type="like"]');
                        const dislikeBtn = box.querySelector('button[data-vote-type="dislike"]');
                        likeBtn.classList.toggle('active-btn', data.vote_state === 'like');
                        dislikeBtn.classList.toggle('active-btn', data.vote_state === 'dislike');
                    }
                });
            });
        });
    }
})();