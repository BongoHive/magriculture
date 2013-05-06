// Possible configuration items:
//
// * translation.<lang>:
//     Jed translation JSON for language (e.g. sw). Optional. If ommitted,
//     untranslated strings are used.
//
// * config:
//     * default_lang:
//         Default language. Default is 'en'.
//     * lima_links_api:
//         Dictionary of username, password and url of the Lima Links API.
//         If ommitted, the dummy API is used instead.
//     * sms_tag:
//         Two element list of [pool, tag] giving the Go endpoint to send SMSes
//         out via. If ommitted, SMSes are not sent.
//     * metric_store:
//         Name of the metric store to use. If omitted, metrics are sent
//         to the metric store named 'default'.
//
// Metrics produced:
//
// * ussd_sessions
// * unique_users
// * first_session_completed
// * second_session_completed
// * sessions_taken_to_register (average)
// * session_new_in.<state-name>
// * session_closed_in.<state-name>
// * possible_timeout_in.<state-name>
// * state_entered.<state-name>
// * state_exited.<state-name>

var vumigo = require("vumigo_v01");
var jed = require("jed");

if (typeof api === "undefined") {
    // testing hook (supplies api when it is not passed in by the real sandbox)
    var api = this.api = new vumigo.dummy_api.DummyApi();
}

var Promise = vumigo.promise.Promise;
var success = vumigo.promise.success;
var maybe_promise = vumigo.promise.maybe_promise;
var State = vumigo.states.State;
var Choice = vumigo.states.Choice;
var ChoiceState = vumigo.states.ChoiceState;
var LanguageChoice = vumigo.states.LanguageChoice;
var PaginatedChoiceState = vumigo.states.PaginatedChoiceState;
var FreeText = vumigo.states.FreeText;
var EndState = vumigo.states.EndState;
var InteractionMachine = vumigo.state_machine.InteractionMachine;
var StateCreator = vumigo.state_machine.StateCreator;
var JsonApi = vumigo.http_api.JsonApi;


function DummyLimaLinksApi(im) {

    var self = this;

    self.im = im;

    self.FARMERS = {
        '+27885557777': {
            farmer_name: "Farmer Bob",
            crops: [
                ["crop1", "Peas"],
                ["crop2", "Carrots"]
            ],
            markets: [
                ["market1", "Kitwe"],
                ["market2", "Ndola"]
            ],
        },
    };

    self.PRICES = {
        "market1": {
            "crop1": {
                "unit1": {
                    unit_name: "boxes",
                    prices: [1.2, 1.1, 1.5]
                },
                "unit2": {
                    unit_name: "crates",
                    prices: [1.6, 1.7, 1.8]
                }
            }
        },
        "market2": {
            "crop1": {
                "unit1": {
                    unit_name: "boxes",
                    prices: []
                }
            }
        }
    };

    self.HIGHEST_MARKETS = {
        "crop1": [
            ["market1", "Kitwe"],
            ["market2", "Ndola"],
        ],
        "crop2": [
            ["market2", "Ndola"],
        ],
    };

    self.ALL_MARKETS = [
        ["market1", "Kitwe"],
        ["market2", "Ndola"],
        ["market3", "Masala"],
    ];

    self.get_farmer = function(msisdn) {
        var p = new Promise();
        // ignore msisdn and always return the example farmer for testing
        p.callback(self.FARMERS['+27885557777']);
        return p;
    };

    self.price_history = function(market_id, crop_id, limit) {
        var p = new Promise();
        var limit = limit || 10;

        var market = self.PRICES[market_id] || {};
        var crop = market[crop_id] || {};
        var price_data = {};

        for (var unit in crop) {
            price_data[unit] = {
                unit_name: crop[unit].unit_name,
                prices: crop[unit].prices,
            };
        }
        p.callback(price_data);
        return p;
    };

    self.highest_markets = function(crop_id, limit) {
        var p = new Promise();
        var limit = limit || 10;
        var markets = self.HIGHEST_MARKETS[crop_id] || [];
        p.callback(markets.slice(0, limit));
        return p;
    };

    self.all_markets = function(limit) {
        var p = new Promise();
        var limit = limit || 10;
        var markets = self.ALL_MARKETS;
        p.callback(markets.slice(0, limit));
        return p;
    };
}


function LimaLinksApi(im, url, opts) {

    var self = this;

    self.url = url;
    self.json_api = JsonApi(im, opts);

    // in case we need to translate content from the API later
    self.lang = im.user.lang || im.config.default_lang || "en";

    self.api_call = function(method, params) {
        var url = self.url + method;
        return self.json_api.get(url, {params: params});
    };

    self.get_farmer = function(msisdn) {
        return self.api_call("farmer", {
            msisdn: msisdn
        });
    };

    self.price_history = function(market_id, crop_id, limit) {
        return self.api_call("price_history", {
            market: market_id,
            crop: crop_id,
            limit: limit
        });
    };

    self.highest_markets = function(crop_id, limit) {
        return self.api_call("highest_markets", {
            crop: crop_id,
            limit: limit
        });
    };

    self.all_markets = function(limit) {
        return self.api_call("markets", {
            limit: limit
        });
    };
}


function BookletState(name, opts) {

    var self = this;
    opts = opts || {};
    State.call(self, name, opts.handlers);

    self.next = opts.next;
    self.pages = opts.pages; // pages are from 0 -> pages - 1
    self.page_changed = opts.page_changed; // page_changed(self) -> promise

    self.initial_page = opts.initial_page || 0;
    self.buttons = opts.buttons || {"1": -1, "2": +1, "3": "exit"};
    self.footer_text = opts.footer_text || "1 for prev, 2 for next, 3 to end.";

    self.page_text = "No page."

    var orig_on_enter = self.on_enter;
    self.on_enter = function() {
        self.set_current_page(self.im.user, self.initial_page);
        return orig_on_enter();
    };

    self.get_current_page = function(user) {
        var pages = user.pages || {};
        return pages[self.name] || 0;
    };

    self.set_current_page = function(user, page) {
        if (typeof user.pages == 'undefined') {
            user.pages = {};
        }
        user.pages[self.name] = page;
    };

    self.inc_current_page = function(user, amount) {
        var page = self.get_current_page(user) + amount;
        page = page % self.pages;
        if (page < 0) {
            page += self.pages;
        }
        self.set_current_page(user, page);
    };

    self.set_page_text = function(text) {
        self.page_text = text;
    };

    self.input_event = function(content, done) {
        if (!content) { content = ""; }
        content = content.trim();

        var button = self.buttons[content];
        if (typeof button === "undefined") {
            done();
            return;
        }

        var amount = Number(button);
        if (!Number.isNaN(amount)) {
            self.inc_current_page(self.im.user, amount);
            var p = self.page_changed(self);
            p.add_callback(done);
            return;
        }

        if (button !== "exit") {
            done();
            return;
        }

        self.call_possible_function(
            self.next, self, [content],
            function (next) {
                self.im.set_user_state(next);
                self.save_response(content);
                done();
            }
        );
    };

    self.display = function() {
        return self.page_text;
    };
}


function MagriWorker() {
    var self = this;
    StateCreator.call(self, "select_service");

    var _ = new jed({});

    // only allow printable ASCII x20 (space) to x73 (tilde)
    self.non_printable_ascii_re = /[^\x20-\x7E]/g;

    self.clean_text = function(title) {
        // replace non-ASCII characters with ?
        return title.replace(self.non_printable_ascii_re, '?');
    };

    self.lima_links_api = function(im) {
        var cfg = im.config.lima_links_api;
        if (!cfg) {
            im.log("Using dummy Lima Links API.");
            return new DummyLimaLinksApi(im);
        }
        im.log("Using real Lima Links API.");
        var opts = {};
        if (cfg.username) {
            opts.auth = {username: cfg.username, password: cfg.password};
        }
        return new LimaLinksApi(im, cfg.url, opts);
    };

    // Session metrics helper

    self.incr_metric = function(im, metric) {
        var p = new Promise();
        p.add_callback(function (value) {
            im.metrics.fire_max(metric, value);
        });
        im.api.request(
            "kv.incr", {key: "metrics." + metric, amount: 1},
            function(reply) {
                if (reply.success) {
                    p.callback(reply.value);
                }
                else {
                    im.log("Failed to increment metric " + metric + ": " +
                           reply.reason);
                    p.callback(0);
                }
            });
        return p;
    }

    // SMSes

    self.send_sms = function(im, content) {
        var sms_tag = im.config.sms_tag;
        if (!sms_tag) return success(true);
        var p = new Promise();
        im.api.request("outbound.send_to_tag", {
            to_addr: im.user_addr,
            content: content,
            tagpool: sms_tag[0],
            tag: sms_tag[1]
        }, function(reply) {
            p.callback(reply.success);
        });
        return p;
    };

    self.add_summary_item = function(user, section_name, item, value) {
        var summary = self.get_user_item(user, 'summary', {});
        var section = summary[section_name] || {};
        section[item] = value;
        summary[section_name] = section;
        self.set_user_item(user, 'summary', summary);
    };

    self.sorted_keys = function(obj, cmp) {
        var keys = [];
        for (var k in obj) {
            keys.push(k);
        };
        keys.sort(cmp);
        return keys;
    };

    self.sms_session_summary = function(im) {
        var summary = self.get_user_item(im.user, 'summary', {});
        var section_names = self.sorted_keys(summary);
        if (section_names.length === 0) {
            return success(false);
        };
        var lines = [];
        for (var k in section_names) {
            var section_name = section_names[k];
            var section = summary[section_name];
            var item_names = self.sorted_keys(section, function (i1, i2) {
                return section[i2] - section[i1];
            });
            var items = item_names.slice(0, 3).map(function (item_name) {
                return item_name + " K" + section[item_name]; })
            lines.push(section_name + ": " + items.join(", "));
        };
        var msg = lines.join("\n");
        return self.send_sms(im, msg);
    };

    // Session handling

    self.get_user_item = function(user, item, default_value) {
        var custom = user.custom || {};
        var value = custom[item];
        return (typeof value != 'undefined') ? value : default_value;
    };

    self.set_user_item = function(user, item, value) {
        if (typeof user.custom == 'undefined') {
            user.custom = {};
        }
        user.custom[item] = value;
    };

    self.inc_user_item = function(user, item) {
        var value = self.get_user_item(user, item, 0) + 1;
        self.set_user_item(user, item, value);
        return value;
    };

    // IM event callbacks

    self.on_session_new = function(event) {
        var p = self.incr_metric(event.im, 'ussd_sessions');
        p.add_callback(function () {
            return event.im.metrics.fire_inc('session_new_in.' +
                                             event.im.current_state.name);
        });
        p.add_callback(function () {
            return self.inc_user_item(event.im.user, 'ussd_sessions');
        });
        return p;
    };

    self.on_session_close = function(event) {
        var p = event.im.metrics.fire_inc('session_closed_in.' +
                                          event.im.current_state.name);
        if (event.data.possible_timeout) {
            p.add_callback(function () {
                return event.im.metrics.fire_inc('possible_timeout_in.' +
                                                 event.im.current_state.name);
            });
            var timeouts = self.inc_user_item(event.im.user,
                                              'possible_timeouts');
            if (timeouts <= 1) {
                p.add_callback(function () {
                    self.send_sms_first_possible_timeout(event.im);
                });
            }
        }
        return p;
    };

    self.on_new_user = function(event) {
        return self.incr_metric(event.im, 'unique_users');
    };

    self.on_state_enter = function(event) {
        return event.im.metrics.fire_inc('state_entered.' + event.data.state.name);
    };

    self.on_state_exit = function(event) {
        return event.im.metrics.fire_inc('state_exited.' + event.data.state.name);
    };

    // States

    self.add_creator("select_service", function(state_name, im) {
        var _ = im.i18n;
        var lima_links_api = self.lima_links_api(im);
        var p = lima_links_api.get_farmer(im.user_addr);
        p.add_callback(function (farmer) {
            var choices = [
                new Choice("select_crop", _.gettext("Market prices"))
            ];
            return new ChoiceState(
                state_name,
                function (choice) {
                    return choice.value;
                },
                _.translate("Hi %1$s.\n" +
                            "Select a service:"
                           ).fetch(farmer.farmer_name),
                choices,
                _.gettext("Please enter the number of the service.")
            );
        });
        return p;
    });

    self.add_creator("select_crop", function(state_name, im) {
        var _ = im.i18n;
        var lima_links_api = self.lima_links_api(im);
        var p = lima_links_api.get_farmer(im.user_addr);
        p.add_callback(function (farmer) {
            var choices = farmer.crops.map(function (crop) {
                var crop_id = crop[0];
                var crop_name = crop[1];
                return new Choice(crop_id, crop_name);
            });
            return new ChoiceState(
                state_name,
                function (choice) {
                    self.set_user_item(im.user, "chosen_crop_name",
                                       choice.label);
                    return "select_market_list";
                },
                _.gettext("Select a crop:"),
                choices,
                _.gettext("Please enter the number of the crop.")
            );
        });
        return p;
    });

    self.add_creator("select_market_list", function(state_name, im) {
        var _ = im.i18n;
        var crop_name = self.get_user_item(im.user, "chosen_crop_name");
        var choices = [
            new Choice("all_markets",
                       _.gettext("All markets")),
            new Choice("best_markets",
                       _.translate("Best markets for %1$s").fetch(crop_name))
        ];
        return new ChoiceState(
            state_name,
            function (choice) {
                // clear chosen_markets list
                self.set_user_item(im.user, "chosen_markets", null);
                return "select_market";
            },
            _.gettext("Select which markets to view:"),
            choices,
            _.gettext("Please select a list of markets.")
        );
    });

    self.add_creator("select_market", function(state_name, im) {
        var _ = im.i18n;
        var p;
        var lima_links_api = self.lima_links_api(im);
        var markets = self.get_user_item(im.user, "chosen_markets");
        if (!markets) {
            var market_list = im.get_user_answer("select_market_list");
            if (market_list == "all_markets") {
                p = lima_links_api.all_markets(10);
            }
            else {
                // if (market_list == "best_markets") {
                var crop_id = im.get_user_answer("select_crop");
                p = lima_links_api.highest_markets(crop_id, 5);
            }
            p.add_callback(function(markets) {
                self.set_user_item(im.user, "chosen_markets", markets);
                return markets;
            });
        }
        else {
            p = success(markets);
        }
        p.add_callback(function (markets) {
            var choices = markets.map(function (crop) {
                var market_id = crop[0];
                var market_name = crop[1];
                return new Choice(market_id, market_name);
            });
            return new ChoiceState(
                state_name,
                function (choice) {
                    var market_idxs = [];
                    markets.forEach(function (elem, i) {
                        if (elem[0] == choice.value) {
                            market_idxs.push(i);
                        }
                    });
                    self.set_user_item(im.user, "chosen_market_idx",
                                       market_idxs[0]);
                    return "show_prices";
                },
                _.gettext("Select a market:"),
                choices,
                _.gettext("Please enter the number of a market.")
            );
        });
        return p;
    });

    self.add_creator("show_prices", function(state_name, im) {
        var _ = im.i18n;
        var lima_links_api = self.lima_links_api(im);

        var crop_id = im.get_user_answer("select_crop");
        var crop_name = self.get_user_item(im.user, "chosen_crop_name");

        var initial_market_idx = self.get_user_item(im.user, "chosen_market_idx");
        var markets = self.get_user_item(im.user, "chosen_markets");

        var next_prev = (markets.length > 1
                         ? _.gettext("Enter 1 for next market," +
                                     " 2 for previous market.") + "\n"
                         : "");
        var exit = _.gettext("Enter 3 to exit.");
        var footer_text = next_prev + exit;

        function page_changed(bookelt) {
            var page = booklet.get_current_page(im.user);
            var market_id = markets[page][0];
            var market_name = markets[page][1];
            var p = lima_links_api.price_history(market_id, crop_id, 5)
            p.add_callback(function(prices) {
                var title = _.translate("Prices of %1$s in %2$s:"
                                       ).fetch(crop_name, market_name);
                var unit_ids = [];
                for (var unit_id in prices) {
                    unit_ids.push(unit_id);
                }
                unit_ids.sort();

                var price_lines = [];
                for (var idx in unit_ids) {
                    var unit_id = unit_ids[idx];
                    var unit_info = prices[unit_id];
                    var unit_prices = unit_info.prices;
                    if (unit_prices.length) {
                        var sum = unit_prices.reduce(function (x, y) {
                            return x + y; });
                        var avg_text = (sum / unit_prices.length).toFixed(2);
                        self.add_summary_item(im.user, crop_name + ", " + unit_info.unit_name,
                                              market_name, avg_text);
                    }
                    else {
                        var avg_text = "-";
                    }
                    price_lines.push("  " + unit_info.unit_name + ": " + avg_text);
                }
                if (!price_lines.length) {
                    price_lines.push("  " + _.gettext("No prices available."));
                }

                var price_text = price_lines.join("\n");
                var text = title + "\n" + price_text + "\n" + next_prev + exit;
                booklet.set_page_text(text);
            });
            return p;
        }

        var booklet = new BookletState(state_name, {
            next: "end",
            pages: markets.length,
            page_changed: page_changed,
            initial_page: initial_market_idx,
            buttons: {"1": -1, "2": +1, "3": "exit"},
            footer_text: footer_text
        });

        var p = page_changed(booklet);
        p.add_callback(function () { return booklet; });
        return p;
    });

    self.add_state(new EndState(
        "end",
        _.gettext("Goodbye!"),
        "select_service",
        {
            on_enter: function() {
                var im = this.im;
                var p = self.sms_session_summary(im);
                return p;
            }
        }
    ));

    self.switch_state = function(state_name, im) {
        if (typeof state_name == "undefined")
            state_name = self.start_state;
        if (!self.state_creators[state_name]) {
            state_name = self.start_state;
        }
        var creator = self.state_creators[state_name];
        return maybe_promise(creator.call(self, state_name, im));
    };
}


// launch app
var states = new MagriWorker();
var im = new InteractionMachine(api, states);
im.attach();
