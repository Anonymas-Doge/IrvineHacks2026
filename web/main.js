// Simple placeholder functionality
document.getElementById("goButton").addEventListener("click", () => {
  const inputValue = document.getElementById("menuInput").value;
  if (inputValue.trim() === "") {
    alert("Please enter a menu item!");
    return;
  }

  // For now, just log to console
  console.log("Menu entered:", inputValue);

  // TODO: later navigate to next page or fetch data
});