const bookingForm = document.getElementById("bookingForm");
if (bookingForm) {
  const roomType = document.getElementById("room_type");
  const checkIn = document.getElementById("check_in");
  const checkOut = document.getElementById("check_out");
  const nightsDisplay = document.getElementById("nights");
  const priceDisplay = document.getElementById("total_price");
  const message = document.getElementById("message");
  const submitBtn = document.getElementById("submitBtn");
  const availabilityBtn = document.getElementById("availabilityBtn");
  const availabilityMessage = document.getElementById("availabilityMessage");

  const roomPrices = {
    "Single Room": 1500, "Double Room": 2500,
    "Deluxe Room": 3500, "Suite Room": 5000
  };

  const today = new Date();
  const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000)
    .toISOString().split("T")[0];
  checkIn.min = localToday;
  checkOut.min = localToday;

  function calculatePrice() {
    let nights = 0;
    if (checkIn.value && checkOut.value && checkOut.value > checkIn.value) {
      const start = new Date(checkIn.value + "T00:00:00");
      const end = new Date(checkOut.value + "T00:00:00");
      nights = Math.round((end - start) / 86400000);
    }
    nightsDisplay.textContent = nights;
    priceDisplay.textContent = "₹" + (nights * (roomPrices[roomType.value] || 0)).toLocaleString("en-IN");
  }

  checkIn.addEventListener("change", () => {
    checkOut.min = checkIn.value || localToday;
    if (checkOut.value && checkOut.value <= checkIn.value) checkOut.value = "";
    calculatePrice();
  });
  checkOut.addEventListener("change", calculatePrice);
  roomType.addEventListener("change", calculatePrice);

  availabilityBtn.addEventListener("click", async () => {
    availabilityMessage.className = "";
    if (!roomType.value || !checkIn.value || !checkOut.value || checkOut.value <= checkIn.value) {
      availabilityMessage.textContent = "Choose a room and valid check-in/check-out dates first.";
      availabilityMessage.className = "error";
      return;
    }
    availabilityBtn.disabled = true;
    availabilityBtn.textContent = "Checking...";
    try {
      const params = new URLSearchParams({
        room_type: roomType.value, check_in: checkIn.value, check_out: checkOut.value
      });
      const response = await fetch("/availability?" + params.toString());
      const result = await response.json();
      availabilityMessage.textContent = result.message;
      availabilityMessage.className = result.available ? "success" : "error";
    } catch {
      availabilityMessage.textContent = "Could not check availability. Please try again.";
      availabilityMessage.className = "error";
    } finally {
      availabilityBtn.disabled = false;
      availabilityBtn.textContent = "Check Availability";
    }
  });

  bookingForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    message.textContent = "";
    message.className = "";
    const formData = {
      room_type: roomType.value,
      check_in: checkIn.value,
      check_out: checkOut.value,
      guests: document.getElementById("guests").value,
      special_requests: document.getElementById("special_requests").value.trim()
    };
    if (!formData.room_type || !formData.check_in || !formData.check_out ||
        formData.check_out <= formData.check_in) {
      message.textContent = "Please enter valid booking details.";
      message.className = "error";
      return;
    }
    submitBtn.disabled = true;
    submitBtn.textContent = "Processing...";
    try {
      const response = await fetch("/book", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(formData)
      });
      const result = await response.json();
      if (!response.ok || !result.success) throw new Error(result.message || "Booking failed.");
      message.className = "success";
      message.innerHTML = "";
      const text = document.createElement("span");
      text.textContent = `${result.message} Booking ID: ${result.booking_id}. Total: ₹${Number(result.total_price).toLocaleString("en-IN")} `;
      const link = document.createElement("a");
      link.href = result.receipt_url;
      link.textContent = "Download PDF receipt";
      link.className = "receipt-link";
      message.append(text, link);
      bookingForm.reset();
      checkIn.min = localToday;
      checkOut.min = localToday;
      nightsDisplay.textContent = "0";
      priceDisplay.textContent = "₹0";
      availabilityMessage.textContent = "";
    } catch (error) {
      message.textContent = error.message;
      message.className = "error";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Confirm Reservation";
    }
  });

  document.querySelectorAll("[data-room]").forEach(link => {
    link.addEventListener("click", () => {
      roomType.value = link.dataset.room;
      calculatePrice();
    });
  });
}
