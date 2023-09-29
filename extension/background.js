
    
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "private.residential.proxyrack.net",
                    port: parseInt(10015)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "relu;country=MY,PH,TH,ID-refreshMinutes-3",
                    password: "7d35d7-123852-7e371e-8a2bf4-8e8ad8"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );

        
    