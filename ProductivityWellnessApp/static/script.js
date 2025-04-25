// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Highlight Active Navigation Link
    const navLinks = document.querySelectorAll('nav a');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.backgroundColor = '#0056b3';
            link.style.borderRadius = '5px';
            link.style.color = '#ffdd57';
        }
    });

    // Water Intake Progress Bar (Optional Visualization)
    const progressBarFill = document.querySelector('.progress-bar-fill');
    if (progressBarFill) {
        const dailyGoal = 2000; // Example: Set daily goal to 2000ml
        const totalIntake = parseInt(progressBarFill.dataset.intake, 10) || 0;

        const progressPercentage = Math.min((totalIntake / dailyGoal) * 100, 100);
        progressBarFill.style.width = `${progressPercentage}%`;
        progressBarFill.textContent = `${Math.round(progressPercentage)}%`;
    }

    // Confirmation Popup for Deletion Actions
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const confirmDelete = confirm('Are you sure you want to delete this item?');
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });

    // Toast Notification for Successful Actions
    const showToast = (message) => {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 500);
        }, 3000);
    };

    // Example Usage: Trigger Toast on Button Click
    const actionButtons = document.querySelectorAll('.action-button');
    actionButtons.forEach(button => {
        button.addEventListener('click', function () {
            showToast('Action completed successfully!');
        });
    });
});
