

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
        this.pgbElement.setAttribute("aria-label", data.status.percent + "% Complete");
        this.pgbElement.setAttribute("style", "width: " + data.status.percent + "%;");
        
        let percent = data.status.percent;
        if (data.status.detail) {
            this.detailElement.innerHTML = data.status.detail;
        } else {
            this.detailElement.innerHTML = percent + "% of 100% completed";
        }

        this.valueElement.innerHTML = percent + "%";
        
        return done;
    }
}