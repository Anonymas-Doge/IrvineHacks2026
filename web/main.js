// Handle Search Input (Pressing Enter)
document.getElementById("menuInput").addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    const inputValue = e.target.value.trim();
    if (!inputValue) {
      alert("Please enter a menu item!");
      return;
    }
    console.log("Searching for:", inputValue);
    localStorage.setItem("menuInput", inputValue);
    // window.location.href = "recipes.html"; // Uncomment when ready
  }
});

// Handle Category Button Clicks
const tags = document.querySelectorAll(".tag-btn");
tags.forEach(tag => {
  tag.addEventListener("click", () => {
    const category = tag.getAttribute("data-category");
    console.log(`Quick filter selected: ${category}`);
    
    // Optional: Auto-fill search or navigate
    document.getElementById("menuInput").value = category;
  });
});

// Handle Nav Links
const navLinks = document.querySelectorAll(".nav-link");
navLinks.forEach(link => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    console.log(`Navigating to: ${e.target.innerText}`);
  });
});