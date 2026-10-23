/*
Report dashboard content height to the CO-OP portal so it can adjust the dashboard iframe height.
*/

(function () {
    "use strict";

    const portalOrigin = "https://icprbcoop.org";
    let lastHeight = 0;
    let resizeTimer;

    // Send height updates only when the dashboard is embedded
    if (window.parent === window) {
        return;
    }

    function reportHeight() {
        const page = document.querySelector(".dashboard-page");

        if (!page) {
            return;
        }

        const pageStyle = window.getComputedStyle(page);
        let contentBottom = page.getBoundingClientRect().top;

        // Measure normal page content without including fixed popup windows
        Array.from(page.children).forEach(function (child) {
            const childStyle = window.getComputedStyle(child);

            if (
                childStyle.display === "none" ||
                childStyle.position === "fixed" ||
                childStyle.position === "absolute"
            ) {
                return;
            }

            const childBottom =
                child.getBoundingClientRect().bottom +
                (parseFloat(childStyle.marginBottom) || 0);

            contentBottom = Math.max(contentBottom, childBottom);
        });

        const height = Math.max(
            200,
            Math.ceil(
                contentBottom +
                window.scrollY +
                (parseFloat(pageStyle.paddingBottom) || 0)
            )
        );

        // Avoid repeated messages for the same height
        if (Math.abs(height - lastHeight) < 2) {
            return;
        }

        lastHeight = height;

        window.parent.postMessage(
            {
                type: "dashboard:resize",
                height: height
            },
            portalOrigin
        );
    }

    function scheduleHeightUpdate() {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(reportHeight, 100);
    }

    function startHeightReporting() {
        const observedElements = new WeakSet();
        const resizeObserver = new ResizeObserver(scheduleHeightUpdate);

        function observeDashboard() {
            const page = document.querySelector(".dashboard-page");

            if (!page) {
                return;
            }

            // Observe the page and its main content sections
            [page, ...page.children].forEach(function (element) {
                if (!observedElements.has(element)) {
                    resizeObserver.observe(element);
                    observedElements.add(element);
                }
            });
        }

        // Detect tab changes and other updates made by Dash
        const mutationObserver = new MutationObserver(function () {
            observeDashboard();
            scheduleHeightUpdate();
        });

        mutationObserver.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            characterData: true
        });

        window.addEventListener("resize", scheduleHeightUpdate);
        document.addEventListener("load", scheduleHeightUpdate, true);

        observeDashboard();
        scheduleHeightUpdate();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", startHeightReporting);
    } else {
        startHeightReporting();
    }
})();