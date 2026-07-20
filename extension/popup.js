document.addEventListener('DOMContentLoaded', () => {
  const goalInput = document.getElementById('goalInput');
  const saveBtn = document.getElementById('saveBtn');
  const status = document.getElementById('status');

  // Load the previously saved goal if it exists
  chrome.storage.local.get(['studyGoal'], (result) => {
    if (result.studyGoal) {
      goalInput.value = result.studyGoal;
    }
  });

  // Save the new goal when clicked
  saveBtn.addEventListener('click', () => {
    const goal = goalInput.value.trim();
    chrome.storage.local.set({ studyGoal: goal }, () => {
      status.textContent = "Goal updated successfully!";
      setTimeout(() => { status.textContent = ""; }, 2000);
    });
  });
});