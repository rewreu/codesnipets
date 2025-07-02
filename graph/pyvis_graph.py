from pyvis.network import Network
import pandas as pd

# — your edge list: either load from CSV or use your DataFrame directly
# df = pd.read_csv("edges.csv")
df = pd.DataFrame([
    {"src": "A", "dst": "B", "edge_weight": 1, "edge_text": "AccountID\naddress"},
    {"src": "B", "dst": "C", "edge_weight": 125, "edge_text": "Address\nIP\nEmployer\nWorkPhone"},
    # …
])

def generate_pyvis_html_with_toggle(df, output_html="graph_with_toggle.html"):
    # 1) Build the pyvis graph
    net = Network(height="750px", width="100%", directed=True)

    # add all nodes
    for n in set(df.src).union(df.dst):
        net.add_node(n, label=str(n))

    # add edges, giving each an explicit id and storing both weight/text
    for idx, row in df.iterrows():
        net.add_edge(
            row.src,
            row.dst,
            id=idx,
            label=str(row.edge_weight),           # initial label = weight
            edge_weight=row.edge_weight,
            edge_text=row.edge_text,
        )

    # 2) Generate the base HTML
    html = net.generate_html()

    # 3) Define toggle button + JS
    toggle_snippet = """
    <!-- === STYLES === -->
    <style>
    #controls {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 999;
        background: white;
        padding: 8px;
        border-radius: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        font-family: sans-serif;
    }
    .switch {
        position: relative;    /* ← add this line */
        display: inline-block;
        width: 50px;
        height: 24px;
        vertical-align: middle;
    }
    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    .slider {
        position: absolute;    /* now positioned relative to .switch */
        cursor: pointer;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: #ccc;
        transition: .4s;
        border-radius: 24px;
    }
    .slider:before {
        position: absolute;
        content: "";
        height: 18px;
        width: 18px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }
    input:checked + .slider {
        background-color: #4CAF50;
    }
    input:checked + .slider:before {
        transform: translateX(26px);
    }
    /* align the little label */
    #toggle-label {
        margin-left: 8px;
        vertical-align: middle;
    }
    /* spacing for sliders */
    #controls label {
        display: block;
        margin-top: 8px;
    }
    </style>

    <!-- === CONTROLS HTML === -->
    <div id="controls">
    <!-- toggle switch -->
    <label>
        <span class="switch">
        <input type="checkbox" id="toggle-switch">
        <span class="slider"></span>
        </span>
        <span id="toggle-label">Show Text</span>
    </label>

    <!-- edge font size slider -->
    <label>
        Edge font size:
        <input type="range" id="edge-font-slider" min="8" max="40" value="14">
        <span id="edge-font-value">14</span>px
    </label>

    <!-- node size slider -->
    <label>
        Node size:
        <input type="range" id="node-size-slider" min="10" max="100" value="25">
        <span id="node-size-value">25</span>px
    </label>
    </div>

    <!-- === SCRIPT === -->
    <script>
    function initNetworkControls(net) {
    const E    = net.body.data.edges;
    const N    = net.body.data.nodes;
    const origE = E.get();
    const origN = N.get();

    const toggle = document.getElementById('toggle-switch');
    const lbl    = document.getElementById('toggle-label');
    const eSld   = document.getElementById('edge-font-slider');
    const eVal   = document.getElementById('edge-font-value');
    const nSld   = document.getElementById('node-size-slider');
    const nVal   = document.getElementById('node-size-value');

    function updateEdges() {
        const size = parseInt(eSld.value, 10);
        eVal.textContent = size;
        const showText = toggle.checked;

        origE.forEach(e => {
        const txt = showText ? e.edge_text : e.edge_weight;
        E.update({ id: e.id, label: String(txt), font: { size } });
        });

        lbl.textContent = showText ? 'Show Weight' : 'Show Text';
    }

    function updateNodes() {
        const sz = parseInt(nSld.value, 10);
        nVal.textContent = sz;
        origN.forEach(n => N.update({ id: n.id, size: sz }));
    }

    toggle.addEventListener('change', updateEdges);
    eSld  .addEventListener('input',  updateEdges);
    nSld  .addEventListener('input',  updateNodes);

    // initial render
    updateEdges();
    updateNodes();
    }

    // invoke once the network exists
    initNetworkControls(window.network);
    </script>


    """

    # 4) Inject the button right before </body>
    html = html.replace("</body>", toggle_snippet + "\n</body>")

    # 5) Write out
    with open("graph_with_toggle.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("► open graph_with_toggle.html in your browser")

generate_pyvis_html_with_toggle(df)
