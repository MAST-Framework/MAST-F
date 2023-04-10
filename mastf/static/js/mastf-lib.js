
REST = {
    doGet: function(url, onsuccess, error = null) {
        $.ajax(url, {
            method: 'GET',
            success: onsuccess,
            error: error,
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
    },

    post: function(url, data, onsuccess, contentType = "application/json", error = null) {
        $.ajax(url, {
            method: 'POST',
            success: onsuccess,
            data: data,
            contentType: contentType,
            error: error,
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
    }
}

Utils = {
    getValue: function(selector) {
        element = $(selector);
        if (selector === undefined) {
            // Display error messages (NOT IMPLEMENTED)
            console.error("Could not locate Element: " + selector);
            return null;
        }
        return element.attr('value')
    } 
}

/**
 * Simple object that defines utility methods when loading information
 * on a single vulnerability. By calling the "load" function, template
 * details, veulnerability details and the target source code will be 
 * fetched from the REST API
 */
Vulnerability = {

    load: function(element) {
        template_id = Utils.getValue('#vuln-template-id-row-' + element.getAttribute('counter'));
        finding_id = Utils.getValue('#vuln-id-row-' + element.getAttribute('counter'));
        scanner_name = Utils.getValue('#scanner-name');
        scan_id = Utils.getValue('#scan-id');

        REST.doGet("/api/v1/finding/template/" + template_id, function(data) {
            document.getElementById('vuln-info-text').innerHTML = data.description

            title = $('#vuln-title')
            title.html(data.title);
            title.attr('href', "/web/details/" + data.article);
        });

        REST.doGet("/api/v1/finding/vulnerability/" + finding_id, function(data) {
            console.log(data);
            Vulnerability.setSeverity(data.severity);
            $('#vuln-details-dropdown').html(data.state);
            $('#vuln-language').html(data.snippet?.language);
            $('#vuln-details-file-size').html(data.snippet?.file_size);
        });

        REST.doGet("/api/v1/code/" + finding_id, function(data) {
            $('#vuln-code').html(data.code);

            let theme_name = 'enlighter';
            if (params.theme == 'dark') {
                theme_name = 'dracula';
            }
            
            EnlighterJS.init('pre', 'code.vuln_code', {
                language : data.language.toLowerCase(),
                theme: theme_name,
                indent : 2,
                textOverflow: 'scroll'
            });
        });

        $('#vuln-card').removeClass('visually-hidden');
    },

    applyVulnerabilityState: function(element) {
        
    },

    /**
     * Applies a progress bar color and width according to the 
     * provided severity.
     * 
     * @param {string} severity the current severity string
     */
    setSeverity(severity) {
        pgbar = $('#vuln-severity');
        element = $('#vuln-severity-badge');

        element.html(severity);
        switch (severity.toLowerCase()) {
            case "high":
                pgbar.attr("style", "width: 80%");
                pgbar.attr("class", "progress-bar bg-red");
                element.attr("class", "badge bg-red-lt");
                break;
        
            case "critical":
                pgbar.attr("style", "width: 100%");
                pgbar.attr("class", "progress-bar bg-pink");
                element.attr("class", "badge bg-pink-lt");
                break;

            case "medium":
                pgbar.attr("style", "width: 50%");
                pgbar.attr("class", "progress-bar bg-orange");
                element.attr("class", "badge bg-orange-lt");
                break;

            case "low":
                pgbar.attr("style", "width: 30%");
                pgbar.attr("class", "progress-bar bg-yellow");
                element.attr("class", "badge bg-yellow-lt");
                break;
            
            default:
                pgbar.attr("style", "width: 0%");
                pgbar.attr("class", "progress-bar bg-secondary");
                element.attr("class", "badge bg-secondary-lt");
                break;
        }
    }

};

class ScanTaskProgressBar {

    static create(backendUrl, options) {
        const progressBar = new this(backendUrl, options);
        progressBar.connect();
    }

    constructor(backendUrl, options) {
        this.url = backendUrl;
        
        var options = options || {};
        let task_id = options.task_id;
        if (task_id === undefined) {
            console.error('[CRITICAL] Invalid task ID');
            return;
        }
        this.interval = options.interval || 2000;

        this.pgbElement = document.getElementById("process-pgb-" + task_id);
        this.statusElement = document.getElementById("process-indicator-" + task_id);
        this.detailElement = document.getElementById("process-pgb-text-" + task_id);
        this.valueElement = document.getElementById("process-pgb-value-" + task_id);

        this.onException = options.onException || this.onError;
    }

    async start() {
        let response;

        try {
            response = await(fetch(this.url));
        } catch(netError) { 
            this.onException(error);
            throw netError;
        }

        if (response.status == 200) {
            let data;
            try {
                data = await response.json();
            } catch(jsonError) { 
                this.onException(jsonError);
                throw jsonError;
            }

            const completed = this.onData(data);
            if (completed === false) {
                setTimeout(this.connect.bind(this), this.interval);
            }
        }
    }

    onError(error) {
        console.error(error);
    }

    onData(data) {
        let done = data.status.completed;
        this.pgbElement.setAttribute("aria-valuenow", data.status.current);
        this.pgbElement.setAttribute("aria-label", data.status.current + "% Complete");
        this.pgbElement.setAttribute("style", "width: " + data.status.current + "%;");
        
        let percent = data.status.current;
        if (data.status.detail) {
            this.detailElement.innerHTML = data.status.detail;
        } else {
            this.detailElement.innerHTML = percent + "% of 100% completed";
        }

        this.valueElement.innerHTML = percent + "%";
        
        return done;
    }
}


