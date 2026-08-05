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
"""