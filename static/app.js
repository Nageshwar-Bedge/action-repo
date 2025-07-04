async function fetchEvents() {
  const res = await fetch('/events');
  const data = await res.json();
  const container = document.getElementById('events');
  container.innerHTML = '';

  data.forEach(event => {
    const div = document.createElement('div');
    const time = new Date(event.timestamp).toUTCString();

    if (event.event_type === "PUSH") {
      div.textContent = `${event.author} pushed to ${event.to_branch} on ${time}`;
    } else if (event.event_type === "PULL_REQUEST") {
      div.textContent = `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${time}`;
    } else if (event.event_type === "MERGE") {
      div.textContent = `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${time}`;
    }

    container.appendChild(div);
  });
}

setInterval(fetchEvents, 15000);
fetchEvents();
