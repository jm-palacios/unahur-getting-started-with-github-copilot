document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // build participants section (bullet list or placeholder)
        const participantsHTML = details.participants.length
          ? `<ul class="participants-list">${details.participants
              .map(
                p =>
                  `<li>${p} <span class="remove-participant" data-activity="${name}" data-email="${p}">&times;</span></li>`
              )
              .join("")}</ul>`
          : `<p class="no-participants">No participants yet.</p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <p><strong>Participants:</strong></p>
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // refresh list to show new participant
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Delegate clicks on delete icons
  activitiesList.addEventListener("click", async (e) => {
    if (e.target && e.target.matches(".remove-participant")) {
      const activityName = e.target.dataset.activity;
      const email = e.target.dataset.email;

      try {
        const resp = await fetch(
          `/activities/${encodeURIComponent(activityName)}/withdraw?email=${encodeURIComponent(
            email
          )}`,
          { method: "POST" }
        );

        const data = await resp.json();
        if (resp.ok) {
          messageDiv.textContent = data.message;
          messageDiv.className = "success";
          fetchActivities(); // refresh list
        } else {
          messageDiv.textContent = data.detail || "Unable to remove participant";
          messageDiv.className = "error";
        }
      } catch (err) {
        console.error("Error removing participant:", err);
        messageDiv.textContent = "Failed to update registration.";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    }
  });

  // Initialize app
  fetchActivities();
});
