/* Live signal block: runs this essay's own model in the reader's browser.
 *
 * Nothing here reimplements the maths. The page carries the contents of sm/
 * and model/ping.py in a <script type="application/json"> written at render
 * time, this file loads Pyodide, drops those files into its virtual
 * filesystem and imports them — so what the reader drives is the same code
 * that produced the static figures further up the page.
 *
 * Cost: Pyodide plus numpy, matplotlib and soundfile is a large download, so
 * it is fetched only when the block is first scrolled near.
 */
(function () {
  "use strict";

  var PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/";
  var PACKAGES = ["numpy", "matplotlib", "soundfile"];

  var root = document.getElementById("live-ping");
  var sourceEl = document.getElementById("live-ping-source");
  if (!root || !sourceEl) return;

  var el = function (role) { return root.querySelector('[data-role="' + role + '"]'); };
  var status = el("status");
  var controls = el("controls");
  var plot = el("plot");
  var audio = el("audio");
  var f0Input = el("f0");
  var decayInput = el("decay");
  var f0Out = el("f0-out");
  var decayOut = el("decay-out");

  var pyodide = null;
  var rendering = false;
  var pending = false;

  function say(message, isError) {
    status.textContent = message;
    status.hidden = false;
    status.classList.toggle("is-error", !!isError);
  }

  // Python side: import the real modules, then hand back a PNG and a WAV.
  var DRIVER = [
    "import base64, io, sys",
    "sys.path[:0] = ['/session', '/session/model']",
    "import matplotlib",
    "matplotlib.use('AGG')",
    "import matplotlib.pyplot as plt",
    "from sm import io as sm_io, plot as sm_plot",
    "from ping import ping",
    "",
    "def render(f0, decay):",
    "    y = ping(f0=f0, decay=decay)",
    "    fig = sm_plot.waveform(y, t_max=0.02)",
    "    buf = io.BytesIO()",
    "    fig.savefig(buf, format='png', dpi=120)",
    "    plt.close(fig)",
    "    return (base64.b64encode(buf.getvalue()).decode(),",
    "            base64.b64encode(sm_io.wav_bytes(y)).decode())",
  ].join("\n");

  function writeSources(py, files) {
    Object.keys(files).forEach(function (path) {
      var full = "/session/" + path;
      var dir = full.slice(0, full.lastIndexOf("/"));
      // mkdir is not recursive and throws if the directory already exists.
      dir.split("/").slice(1).reduce(function (sofar, part) {
        var next = sofar + "/" + part;
        try { py.FS.mkdir(next); } catch (e) { /* already there */ }
        return next;
      }, "");
      py.FS.writeFile(full, files[path]);
    });
  }

  async function boot() {
    try {
      say("Fetching Python — this is a few megabytes, once.");
      var mod = await import(PYODIDE_URL + "pyodide.mjs");
      pyodide = await mod.loadPyodide({ indexURL: PYODIDE_URL });

      say("Loading numpy, matplotlib and soundfile…");
      await pyodide.loadPackage(PACKAGES);

      writeSources(pyodide, JSON.parse(sourceEl.textContent));
      pyodide.runPython(DRIVER);

      status.hidden = true;
      controls.hidden = false;
      await draw();
    } catch (err) {
      say("Could not start Python in this browser: " + err, true);
    }
  }

  async function draw() {
    if (!pyodide) return;
    if (rendering) { pending = true; return; }
    rendering = true;
    try {
      var result = pyodide.globals.get("render")(
        parseFloat(f0Input.value),
        parseFloat(decayInput.value)
      );
      var png = result.get(0);
      var wav = result.get(1);
      result.destroy();
      plot.src = "data:image/png;base64," + png;
      audio.src = "data:audio/wav;base64," + wav;
    } catch (err) {
      say("Render failed: " + err, true);
    } finally {
      rendering = false;
      if (pending) { pending = false; draw(); }
    }
  }

  function readout() {
    f0Out.textContent = f0Input.value + " Hz";
    decayOut.textContent = parseFloat(decayInput.value).toFixed(1) + " /s";
  }

  // Slider drags fire continuously; coalesce them so we render once the hand
  // settles rather than queueing a plot per pixel.
  var timer = null;
  function onInput() {
    readout();
    clearTimeout(timer);
    timer = setTimeout(draw, 150);
  }

  [f0Input, decayInput].forEach(function (input) {
    input.addEventListener("input", onInput);
  });
  readout();

  if ("IntersectionObserver" in window) {
    var seen = new IntersectionObserver(function (entries, obs) {
      if (entries.some(function (e) { return e.isIntersecting; })) {
        obs.disconnect();
        boot();
      }
    }, { rootMargin: "400px" });
    seen.observe(root);
  } else {
    boot();
  }
})();
