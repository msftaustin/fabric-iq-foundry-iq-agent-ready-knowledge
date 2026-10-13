(function () {
  "use strict";

  const mount = document.querySelector("#walkthrough");
  const walkthrough = window.WALKTHROUGH;

  if (!mount) {
    return;
  }
  if (!walkthrough || !Array.isArray(walkthrough.steps) || walkthrough.steps.length === 0) {
    mount.textContent = "This walkthrough does not contain any steps.";
    return;
  }

  const state = {
    index: 0,
    notesVisible: false
  };

  const create = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) {
      element.className = className;
    }
    if (text !== undefined) {
      element.textContent = text;
    }
    return element;
  };

  const heading = create("header", "demo-heading");
  heading.append(create("h1", "demo-title", walkthrough.title || "Demo walkthrough"));
  if (walkthrough.subtitle) {
    heading.append(create("p", "demo-subtitle", walkthrough.subtitle));
  }

  const progress = create("div", "demo-progress");
  const card = create("main", "demo-card");
  card.setAttribute("aria-live", "polite");
  const count = create("p", "demo-count");
  const title = create("h2", "demo-step-title");
  const figure = create("figure", "demo-figure");
  const image = create("img", "demo-image");
  const caption = create("figcaption", "demo-caption");
  figure.append(image, caption);
  const content = create("div", "demo-content");
  const notes = create("aside", "demo-notes");
  card.append(count, title, figure, content, notes);

  const controls = create("nav", "demo-controls");
  controls.setAttribute("aria-label", "Walkthrough controls");
  const previous = create("button", "demo-button", "Previous");
  const toggleNotes = create("button", "demo-button demo-button-secondary", "Presenter notes");
  const next = create("button", "demo-button", "Next");
  for (const button of [previous, toggleNotes, next]) {
    button.type = "button";
  }
  controls.append(previous, toggleNotes, next);
  mount.append(heading, progress, card, controls);

  const stepButtons = walkthrough.steps.map((step, index) => {
    const button = create("button", "demo-progress-step", String(index + 1));
    button.type = "button";
    button.setAttribute("aria-label", `Open step ${index + 1}: ${step.title || ""}`);
    button.addEventListener("click", () => navigate(index));
    progress.append(button);
    return button;
  });

  const bounded = (index) => Math.min(walkthrough.steps.length - 1, Math.max(0, index));

  const indexFromLocation = () => {
    const match = window.location.hash.match(/^#step-(\d+)$/);
    return match ? bounded(Number(match[1]) - 1) : 0;
  };

  const render = (index) => {
    state.index = bounded(index);
    const step = walkthrough.steps[state.index];
    count.textContent = `Step ${state.index + 1} of ${walkthrough.steps.length}`;
    title.textContent = step.title || "";
    content.innerHTML = step.body || "";

    if (step.image) {
      image.src = step.image;
      image.alt = step.imageAlt || step.title || "";
      caption.textContent = step.imageAlt || "";
      figure.hidden = false;
    } else {
      image.removeAttribute("src");
      figure.hidden = true;
    }

    notes.textContent = step.notes || "";
    notes.hidden = !state.notesVisible || !step.notes;
    toggleNotes.hidden = !step.notes;
    toggleNotes.setAttribute("aria-pressed", String(state.notesVisible));
    previous.disabled = state.index === 0;
    next.disabled = state.index === walkthrough.steps.length - 1;

    stepButtons.forEach((button, buttonIndex) => {
      button.classList.toggle("is-current", buttonIndex === state.index);
      if (buttonIndex === state.index) {
        button.setAttribute("aria-current", "step");
      } else {
        button.removeAttribute("aria-current");
      }
    });
  };

  const navigate = (index) => {
    const destination = bounded(index);
    window.history.replaceState(null, "", `#step-${destination + 1}`);
    render(destination);
  };

  previous.addEventListener("click", () => navigate(state.index - 1));
  next.addEventListener("click", () => navigate(state.index + 1));
  toggleNotes.addEventListener("click", () => {
    state.notesVisible = !state.notesVisible;
    render(state.index);
  });
  window.addEventListener("hashchange", () => render(indexFromLocation()));
  document.addEventListener("keydown", (event) => {
    if (event.target && ["INPUT", "SELECT", "TEXTAREA"].includes(event.target.tagName)) {
      return;
    }
    const actions = {
      ArrowLeft: () => navigate(state.index - 1),
      ArrowRight: () => navigate(state.index + 1),
      Home: () => navigate(0),
      End: () => navigate(walkthrough.steps.length - 1),
      n: () => toggleNotes.click(),
      N: () => toggleNotes.click()
    };
    if (actions[event.key]) {
      actions[event.key]();
      event.preventDefault();
    }
  });

  document.title = walkthrough.title || document.title;
  render(indexFromLocation());
})();
