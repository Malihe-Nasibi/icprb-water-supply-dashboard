# Dropdown styles

DROPDOWN_TITLE_STYLE = {
    "fontWeight": "bold",
    "fontSize": "20px",
    "color": "#1f2d3d",
    "marginBottom": "8px",
    "display": "block"
}

DROPDOWN_CLASS_NAME = "dashboard-dropdown"

DROPDOWN_CSS = """
.dashboard-dropdown,
.dashboard-dropdown * {
    font-size: 21px !important;
    font-weight: 800 !important;
}

.dashboard-dropdown .Select-control {
    min-height: 50px !important;
}

.dashboard-dropdown .Select-placeholder,
.dashboard-dropdown .Select-value,
.dashboard-dropdown .Select-value-label {
    line-height: 50px !important;
    font-size: 21px !important;
    font-weight: 800 !important;
}

.dashboard-dropdown .Select-input,
.dashboard-dropdown .Select-input input {
    height: 50px !important;
    line-height: 50px !important;
    font-size: 21px !important;
    font-weight: 800 !important;
}

.dashboard-dropdown .Select-menu-outer,
.dashboard-dropdown .Select-menu-outer *,
.dashboard-dropdown .VirtualizedSelectOption,
.dashboard-dropdown .Select-option {
    font-size: 21px !important;
    font-weight: 800 !important;
}

/* Streamflow, forecast, and reservoir dropdown styles */

.streamflow-controls > div > label,
.forecast-controls > div > label {
    font-size: clamp(16px, 1.5vw, 20px) !important;
}

.streamflow-controls .dashboard-dropdown,
.streamflow-controls .dashboard-dropdown *,
.forecast-controls .dashboard-dropdown,
.forecast-controls .dashboard-dropdown *,
.reservoir-controls .dashboard-dropdown,
.reservoir-controls .dashboard-dropdown * {
    font-size: clamp(16px, 1.5vw, 21px) !important;
}
"""


# Dashboard menu styles

MENU_CSS = """
#dashboard-tab input[type="radio"] {
    display: none;
}

#dashboard-tab label {
    transition: all 0.18s ease-in-out;
}

#dashboard-tab label:hover {
    background-color: #cfddeb !important;
    border-color: #9fb7cf !important;
    box-shadow:
        inset 1px 1px 2px rgba(255,255,255,0.65),
        inset -2px -2px 4px rgba(0,0,0,0.12),
        0px 5px 10px rgba(0,0,0,0.22) !important;
    transform: translateY(-1px);
}

#dashboard-tab label:has(input[type="radio"]:checked) {
    background: linear-gradient(145deg, #2f5f89, #1f4568) !important;
    color: white !important;
    border-color: #17364f !important;
    font-weight: 900 !important;
    box-shadow:
        inset 2px 2px 3px rgba(255,255,255,0.35),
        inset -3px -3px 5px rgba(0,0,0,0.25),
        0px 6px 12px rgba(0,0,0,0.28) !important;
    transform: translateY(-1px);
}
"""