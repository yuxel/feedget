var feedget = {};
feedget.APIUrl = "http://localhost:8888/jsonp/";
//feedget.APIUrl = "http://api.feedget.net/";
feedget.getFeed = function(url) {
    var script  = document.createElement('script');
    //todo: determine seperator ? or & 
    script.src  = feedget.APIUrl + url;

    script.type = 'text/javascript';
    script.defer = true;

    document.getElementsByTagName('head').item(0).appendChild(script);
}

feedget.errorHandler = function(errorObject) {
    switch(errorObject.code) {
            case "1" : 
                    text = "Feed not valid"; 
                    break;
            case "2" : 
                    text = "Feed not valid"; 
                    break;
            default :
                    text = "Something went wrong";
                    break;
        }
        alert(text);
}

feedget.parser = function(data) {
    feedgetList = document.getElementById("feedgetContainer");
    feedgetList.innerHTML = "";

    if( data.error) {
        feedget.errorHandler(data.error);
        return false;
    }
    else {
        items = data;

        text = "<ul class=\"feedgetList\">";

        for(i=0; i< items.length; i++) {
            title = items[i].title;
            description = items[i].description;
            link = items[i].link;
            feedDate = new Date();
            feedDate.setTime ( items[i].date * 1000 ); //to milliseconds

            dateText = feedDate.toGMTString();

            text += "<li class=\"feedgetItem\">";
            text += "<div class=\"feedgetItemContainer\">";
            text += "<h1 class=\"feedgetHeader\">" + title + "</h1>";
            text += "<span class=\"feedgetDateTime\">" + dateText + "</span>";
            text += "<p class=\"feedgetSummary\">" + description + "</p>";
            text += "<a class=\"feedgetLink\" href=\"" + link + "\">More</a>";
            text += "</div>"
            text += "</li>";
            
        }

        text += "</ul>";
        feedgetList.innerHTML += text;
    }
}

