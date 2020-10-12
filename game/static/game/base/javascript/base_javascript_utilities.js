/* Markdown and latex loader */
const tm = texmath.use(katex);
const md = markdownit().use(tm, {
    engine: katex,
    delimiters: "dollars",
    katexOptions: {macros: {"\\RR": "\\mathbb{R}"}}
});

/* Generate an error message at a given location with given contents */
function errorMessage(type, head, body, location) {
    var sign;
    var color;

    switch (type) {
        case "warning":
            sign = "<svg width=\"1em\" height=\"1em\" viewBox=\"0 0 16 16\" class=\"bi bi-question-diamond-fill\" fill=\"currentColor\" xmlns=\"http://www.w3.org/2000/svg\"><path fill-rule=\"evenodd\" d=\"M9.05.435c-.58-.58-1.52-.58-2.1 0L.436 6.95c-.58.58-.58 1.519 0 2.098l6.516 6.516c.58.58 1.519.58 2.098 0l6.516-6.516c.58-.58.58-1.519 0-2.098L9.05.435zM5.495 6.033a.237.237 0 0 1-.24-.247C5.35 4.091 6.737 3.5 8.005 3.5c1.396 0 2.672.73 2.672 2.24 0 1.08-.635 1.594-1.244 2.057-.737.559-1.01.768-1.01 1.486v.105a.25.25 0 0 1-.25.25h-.81a.25.25 0 0 1-.25-.246l-.004-.217c-.038-.927.495-1.498 1.168-1.987.59-.444.965-.736.965-1.371 0-.825-.628-1.168-1.314-1.168-.803 0-1.253.478-1.342 1.134-.018.137-.128.25-.266.25h-.825zm2.325 6.443c-.584 0-1.009-.394-1.009-.927 0-.552.425-.94 1.01-.94.609 0 1.028.388 1.028.94 0 .533-.42.927-1.029.927z\"/></svg>";
            color = "alert-warning";
            break;
        case "error":
            sign = "<svg width=\"1em\" height=\"1em\" viewBox=\"0 0 16 16\" class=\"bi bi-exclamation-diamond-fill\" fill=\"currentColor\" xmlns=\"http://www.w3.org/2000/svg\"><path fill-rule=\"evenodd\" d=\"M9.05.435c-.58-.58-1.52-.58-2.1 0L.436 6.95c-.58.58-.58 1.519 0 2.098l6.516 6.516c.58.58 1.519.58 2.098 0l6.516-6.516c.58-.58.58-1.519 0-2.098L9.05.435zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z\"/></svg>";
            color = "alert-danger";
            break;
        case "info":
            sign = "<svg width=\"1em\" height=\"1em\" viewBox=\"0 0 16 16\" class=\"bi bi-info-square-fill\" fill=\"currentColor\" xmlns=\"http://www.w3.org/2000/svg\"><path fill-rule=\"evenodd\" d=\"M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm8.93 4.588l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z\"/></svg>";
            color = "alert-info";
            break;
        case "success":
            sign = "<svg width=\"1em\" height=\"1em\" viewBox=\"0 0 16 16\" class=\"bi bi-check-square-fill\" fill=\"currentColor\" xmlns=\"http://www.w3.org/2000/svg\"><path fill-rule=\"evenodd\" d=\"M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm10.03 4.97a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z\"/></svg>";
            color = "alert-success";
            break;
        case "debug":
            sign = "<svg width=\"1em\" height=\"1em\" viewBox=\"0 0 16 16\" class=\"bi bi-gear-fill\" fill=\"currentColor\" xmlns=\"http://www.w3.org/2000/svg\"><path fill-rule=\"evenodd\" d=\"M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 0 0-5.86 2.929 2.929 0 0 0 0 5.858z\"/></svg>";
            color = "alert-primary";
            break;
        default:
            sign = "<svg width=\"1em\" height=\"1em\" viewBox=\"0 0 16 16\" class=\"bi bi-question-square-fill\" fill=\"currentColor\" xmlns=\"http://www.w3.org/2000/svg\"><path fill-rule=\"evenodd\" d=\"M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm3.496 6.033a.237.237 0 0 1-.24-.247C5.35 4.091 6.737 3.5 8.005 3.5c1.396 0 2.672.73 2.672 2.24 0 1.08-.635 1.594-1.244 2.057-.737.559-1.01.768-1.01 1.486v.105a.25.25 0 0 1-.25.25h-.81a.25.25 0 0 1-.25-.246l-.004-.217c-.038-.927.495-1.498 1.168-1.987.59-.444.965-.736.965-1.371 0-.825-.628-1.168-1.314-1.168-.803 0-1.253.478-1.342 1.134-.018.137-.128.25-.266.25h-.825zm2.325 6.443c-.584 0-1.009-.394-1.009-.927 0-.552.425-.94 1.01-.94.609 0 1.028.388 1.028.94 0 .533-.42.927-1.029.927z\"/></svg>";
            color = "alert-secondary";
            break;
    }

    location.append("<div class=\"alert " + color + " alert-dismissible fade show\" role=\"alert\"><strong>" + sign + " " + head + "</strong> " + body + "<button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button></div>");
}

var socket_inactive_message_send = false;

/* Make sure that a socket_connection error is only send once */
function socket_connection_error(location) {
    if (!socket_inactive_message_send) {
        errorMessage("error", "Fout in socket verbinding!", "De meeste onderdelen blijven werken, maar verwacht een iets tragere response.", $("#errorMessage"));
        socket_inactive_message_send = true;
    }
}

/* Reset socket_inactive_message_send */
function socket_connection_succes() {
    socket_inactive_message_send = false;
}

/* Parses the given data into HTML using markdown and Latex syntax and returns the processed content */
function runMarkdownLatex(markdownData) {
    var renderData = $(md.render(markdownData));
    $(renderData).find("img").addClass("img-fluid");
    return $(renderData);
}

/* Parses the given data into HTML using markdown and Latex syntax and loads it into the required destination */
function runMarkdownLatexAtDest(destination, markdownData) {
    $(destination).html(runMarkdownLatex(markdownData));
}

/* Disables a given inputfield for a given time in milliseconds (default 1 second) and replaces its contents with a spinning wheel */
function timeoutSubmitButton(id, timeout = 1000, buttonText = "Laden...") {
    var currentValue = $(id).html();

    /* Disable */
    $(id).prop("disabled", true);
    $(id).html("<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span> " + buttonText);

    /* Enable after timeout */
    setTimeout(function () {
        $(id).prop("disabled", false);
        $(id).html(currentValue);
    }, timeout);
}

/* Update the scorebar with a new value and change visuals accordingly */
function updateScoreBar(obtainedScore, maxScore, id) {
    var scoreBar = $(id);

    obtainedScore = parseInt(obtainedScore);
    maxScore = parseInt(maxScore);

    if (obtainedScore === 0 || maxScore === 0) {
        scoreBar.addClass("bg-secondary").removeClass("bg-succes").attr("aria-valuenow", 100).css("width", 100 + "%").html(0 + "%");
    } else {
        var final = ((obtainedScore / maxScore) * 100).toFixed(0);

        scoreBar.addClass("bg-succes").removeClass("bg-secondary").attr("aria-valuenow", final).css("width", final + "%").html(final + "%");
    }
}

/* Change set the value of a given DOM field to that of the value in a given inputfield on change.
*  If the inputfield is empty, set the provided default value. */
function liveTextUpdate(inputField, target, defaultValue = "") {
    inputField.bind('input propertychange', function () {
        if (inputField.val() !== "")
            target.text(inputField.val());
        else
            target.text(defaultValue);
    });
}

/* Setupt for websockets */
const winloc = window.location;

const protocol = (winloc.protocol === "https:") ? "wss://" : "ws://";

const wsStart = protocol + winloc.host;