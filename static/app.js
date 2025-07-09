function addToShopping(recipeId, recipeName) {
  fetch(`/shopping-list/add-from-recipe/${recipeId}`, { method: "POST" }).then(
    () => {
      const span = document.getElementById(`msg-${recipeId}`);
      if (span) {
        span.textContent = `✔️ Added!`;
        span.style.display = "inline";
        setTimeout(() => {
          span.style.display = "none";
        }, 1000);
      }
    }
  );
}

function toggleCheck(itemId) {
  fetch(`/shopping-list/check/${itemId}`, { method: "POST" }).then(() =>
    window.location.reload()
  );
}

function clearChecked() {
  if (confirm("Are you sure you want to delete all checked items?")) {
    fetch("/shopping-list/clear-checked", { method: "POST" }).then(() =>
      window.location.reload()
    );
  }
}
