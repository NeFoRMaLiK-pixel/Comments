(function () {
  const { createApp } = Vue;

  const CommentNode = {
    name: "comment-node",
    template: "#comment-node-template",
    props: {
      comment: { type: Object, required: true },
      depth: { type: Number, default: 0 },
    },
    methods: {
      formatDate(value) {
        const date = new Date(value);
        return date.toLocaleString();
      },
    },
  };

  createApp({
    components: { CommentNode },
    data() {
      return {
        comments: [],
        previewHtml: "",
        captcha: { key: "", image: "", ttl: 0 },
        pagination: { page: 1, next: null, previous: null },
        sort: { field: "created_at", direction: "desc" },
        loading: { list: false, submit: false },
        errors: { form: "" },
        form: {
          parent: null,
          username: "",
          email: "",
          homepage: "",
          text: "",
          captchaValue: "",
          attachment: null,
        },
        lightbox: { open: false, type: "image", content: "" },
        ws: null,
      };
    },
    mounted() {
      this.reloadCaptcha();
      this.loadComments();
      // this.connectWs();
    },
    beforeUnmount() {
      if (this.ws) {
        this.ws.close();
      }
    },
    methods: {
      getCsrfToken() {
        const cookie = document.cookie
          .split(";")
          .map((item) => item.trim())
          .find((item) => item.startsWith("csrftoken="));
        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
      },
      orderingValue() {
        return this.sort.direction === "desc" ? `-${this.sort.field}` : this.sort.field;
      },
      async loadComments(page = 1) {
        this.loading.list = true;
        this.errors.form = "";

        try {
          const params = new URLSearchParams({
            ordering: this.orderingValue(),
            page: String(page),
          });
          const response = await fetch(`/api/comments/?${params.toString()}`, {
            credentials: "same-origin",
          });

          if (!response.ok) {
            throw new Error("Failed to load comments.");
          }

          const data = await response.json();
          this.comments = data.results || [];
          this.pagination.page = Number(page);
          this.pagination.next = data.next;
          this.pagination.previous = data.previous;
        } catch (error) {
          this.errors.form = error.message;
        } finally {
          this.loading.list = false;
        }
      },
      async reloadCaptcha() {
        const response = await fetch("/api/comments/captcha/", { credentials: "same-origin" });
        const data = await response.json();
        this.captcha = data;
        this.form.captchaValue = "";
      },
      onFileChange(event) {
        this.form.attachment = event.target.files[0] || null;
      },
      setReply(comment) {
        this.form.parent = comment.id;
        window.scrollTo({ top: 0, behavior: "smooth" });
      },
      cancelReply() {
        this.form.parent = null;
      },
      insertTag(tag) {
        const textarea = this.$refs.textArea;
        if (!textarea) {
          return;
        }

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const source = this.form.text;
        const selected = source.slice(start, end);
        const wrapped = `<${tag}>${selected || ""}</${tag}>`;

        this.form.text = source.slice(0, start) + wrapped + source.slice(end);
      },
      insertLink() {
        const href = prompt("Link URL (http/https):", "https://");
        if (!href) {
          return;
        }

        const title = prompt("Link title (optional):", "") || "";
        const textarea = this.$refs.textArea;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const source = this.form.text;
        const selected = source.slice(start, end) || "link";
        const tag = `<a href="${href}" title="${title}">${selected}</a>`;

        this.form.text = source.slice(0, start) + tag + source.slice(end);
      },
      async previewComment() {
        this.errors.form = "";

        try {
          const response = await fetch("/api/comments/preview/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": this.getCsrfToken(),
            },
            credentials: "same-origin",
            body: JSON.stringify({ text: this.form.text }),
          });

          const data = await response.json();
          if (!response.ok) {
            throw new Error(this.extractErrors(data));
          }
          this.previewHtml = data.preview_html;
        } catch (error) {
          this.errors.form = error.message;
        }
      },
      extractErrors(payload) {
        if (typeof payload === "string") {
          return payload;
        }
        if (!payload || typeof payload !== "object") {
          return "Validation error";
        }

        const messages = [];
        for (const [field, value] of Object.entries(payload)) {
          if (Array.isArray(value)) {
            messages.push(`${field}: ${value.join(", ")}`);
          } else {
            messages.push(`${field}: ${value}`);
          }
        }
        return messages.join(" | ");
      },
      async submitComment() {
        this.loading.submit = true;
        this.errors.form = "";

        try {
          const fd = new FormData();
          if (this.form.parent) {
            fd.append("parent", String(this.form.parent));
          }
          fd.append("username", this.form.username);
          fd.append("email", this.form.email);
          fd.append("homepage", this.form.homepage || "");
          fd.append("text", this.form.text);
          fd.append("captcha_key", this.captcha.key);
          fd.append("captcha_value", this.form.captchaValue);
          if (this.form.attachment) {
            fd.append("attachment", this.form.attachment);
          }

          const response = await fetch("/api/comments/", {
            method: "POST",
            headers: {
              "X-CSRFToken": this.getCsrfToken(),
            },
            credentials: "same-origin",
            body: fd,
          });

          const data = await response.json();
          if (!response.ok) {
            throw new Error(this.extractErrors(data));
          }

          this.form.parent = null;
          this.form.text = "";
          this.form.captchaValue = "";
          this.form.attachment = null;
          this.previewHtml = "";
          if (this.$refs.fileInput) {
            this.$refs.fileInput.value = "";
          }

          await this.reloadCaptcha();
          await this.loadComments(this.pagination.page);
        } catch (error) {
          this.errors.form = error.message;
          await this.reloadCaptcha();
        } finally {
          this.loading.submit = false;
        }
      },
      changeSort() {
        this.loadComments(1);
      },
      goNext() {
        if (!this.pagination.next) {
          return;
        }
        const url = new URL(this.pagination.next, window.location.origin);
        this.loadComments(Number(url.searchParams.get("page") || 1));
      },
      goPrev() {
        if (!this.pagination.previous) {
          return;
        }
        const url = new URL(this.pagination.previous, window.location.origin);
        this.loadComments(Number(url.searchParams.get("page") || 1));
      },
      async openAttachment(comment) {
        if (!comment.attachment_url) {
          return;
        }

        if (comment.attachment_type === "image") {
          this.lightbox = { open: true, type: "image", content: comment.attachment_url };
          return;
        }

        if (comment.attachment_type === "text") {
          try {
            const response = await fetch(comment.attachment_url, { credentials: "same-origin" });
            const text = await response.text();
            this.lightbox = { open: true, type: "text", content: text.slice(0, 100000) };
          } catch (error) {
            this.errors.form = "Failed to open attachment.";
          }
        }
      },
      closeLightbox() {
        this.lightbox.open = false;
      },
      connectWs() {
          const protocol = window.location.protocol === "https:" ? "wss" : "ws";
          this.ws = new WebSocket(`${protocol}://${window.location.host}/ws/comments/`);

          this.ws.onmessage = () => {
            this.loadComments(this.pagination.page);
          };

          this.ws.onclose = () => {
            setTimeout(() => this.connectWs(), 1500);
          };
      },
    },
  }).mount("#app");
})();