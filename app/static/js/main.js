document.addEventListener('DOMContentLoaded', function() {

    const deleteForms = document.querySelectorAll('form.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(event) {
             const confirmed = confirm('Вы уверены, что хотите удалить этот пост? Отменить действие будет невозможно.');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });

    const LIKED_POSTS_KEY = 'uptrix_liked_posts';

    function getLikedPosts() {
        const liked = localStorage.getItem(LIKED_POSTS_KEY);
        return liked ? new Set(JSON.parse(liked)) : new Set();
    }

    function saveLikedPost(postId) {
        const likedSet = getLikedPosts();
        likedSet.add(postId);
        localStorage.setItem(LIKED_POSTS_KEY, JSON.stringify(Array.from(likedSet)));
    }

    const likeButtons = document.querySelectorAll('.like-button');
    const likedPostsSet = getLikedPosts();

    likeButtons.forEach(button => {
        const postId = button.dataset.postId;
        const likesCounter = button.closest('.likes-count').querySelector('.like-number');

        if (likedPostsSet.has(postId)) {
            button.disabled = true;
            button.classList.add('liked');
        }

        button.addEventListener('click', function() {
            if (button.disabled) {
                return;
            }

            button.disabled = true;
            button.classList.add('liked');

            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

            fetch(`/like_post/${postId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success' && likesCounter) {
                    likesCounter.textContent = data.likes;
                    saveLikedPost(postId);
                } else {
                    console.error('Like request failed or counter not found:', data.message || 'Unknown error');
                    button.disabled = false;
                    button.classList.remove('liked');
                }
            })
            .catch(error => {
                 console.error('Error sending like request:', error);
                button.disabled = false;
                button.classList.remove('liked');
                alert('Не удалось поставить лайк. Попробуйте позже.');
            });
        });
    });
   
    console.log("uptrixio.onrender.com ready!");})
