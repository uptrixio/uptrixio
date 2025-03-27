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

    console.log("uptrix.io JS loaded!");
});