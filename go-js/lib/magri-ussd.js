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
var BookletState = vumigo.states.BookletState;


function LimaLinksApi(im, url, opts) {

    var self = this;

    self.url = url;
    self.json_api = new JsonApi(im, opts);

    // in case we need to translate content from the API later
    self.lang = im.user.lang || im.config.default_lang || "en";

    self.headers = {
        'Content-Type': ['application/json']
    };

    self.api_call = function(method, params) {
        var url = self.url + method;
        return self.json_api.get(url, {params: params});
    };

    self.api_post = function(method, data) {
        var url = self.url + method;
        return self.json_api.post(url, {data: data, headers: self.headers});
    };

    self.get_farmer = function(username) {
        var p = self.api_call("farmer/", {
            actor__user__username: username
        });
        p.add_callback(function(result){
            if (result.objects.length === 0){
                return null;
            } else {
                return result.objects[0];
            }
        });
        return p;
    };

    self.post_user = function(data) {
        var p = self.api_post("user/", data);
        p.add_callback(function(result){
            // TODO: error checking
            return result;
        });
        return p;
    };

    self.post_farmer = function(data) {
        var p = self.api_post("farmer/", data);
        p.add_callback(function(result){
            // TODO: error checking
            return result;
        });
        return p;
    };

    self.price_history = function(market_id, crop_id, limit) {
        var p =  self.api_call("price_history/", {
            market: market_id,
            crop: crop_id,
            limit: limit
        });
        p.add_callback(function(result){
            return result.objects[0];
        });
        return p;
    };

    self.highest_markets = function(crop_id, limit) {
        var p =  self.api_call("highest_markets/", {
            crop: crop_id,
            limit: limit
        });
        p.add_callback(function(result){
            return result.objects;
        });
        return p;
    };

    self.all_markets = function(limit) {
        var p = self.api_call("markets/", {
            limit: limit
        });
        p.add_callback(function(result){
            return result.objects;
        });
        return p;
    };

    self.all_districts = function() {
        var p = self.api_call("district/", {
            limit: 0
        });
        p.add_callback(function(result){
            return result.objects;
        });
        return p;
    };

    self.all_crops = function() {
        var p = self.api_call("crop/", {
            limit: 0
        });
        p.add_callback(function(result){
            return result.objects;
        });
        return p;
    };
}



function MagriWorker() {
    var self = this;
    StateCreator.call(self, "select_service");

    var _ = new jed({});

    self.lima_links_api = function(im) {
        var cfg = im.config.lima_links_api;
        var opts = {};
        if (cfg.username) {
            opts.auth = {username: cfg.username, password: cfg.password};
        }
        return new LimaLinksApi(im, cfg.url, opts);
    };

    self.findInArray = function(array, what) {
        var indexes = [], what = what.toLowerCase();
        if (!what.length)
            return indexes;
        array.forEach(function(el, index) {
            if (typeof(el) == "string" && el.toLowerCase().indexOf(what)!=-1)
                indexes.push(index);
        });
        return indexes;
    };

    self.extractFieldFromArray = function(arr, field) {
        var extracted = [];
        arr.forEach(function(el, index) {
            if (el[field])
                extracted.push(el[field]);
        });
        return extracted;
    };

    self.get_contact = function(){
        var p = im.api_request('contacts.get_or_create', {
            delivery_class: 'ussd',
            addr: im.user_addr
        });
        return p;
    };

    self.registration_data_collect = function(){
        var crops = [];
        var curr_crops = self.get_user_item(im.user, "registration_crops", []);
        curr_crops.forEach(function(v, i){
            crops.push("/api/v1/crop/" + v + "/");
        });

        var data = {
            user: {
                "username": im.user_addr,
                "first_name": im.get_user_answer('registration_name_first'),
                "last_name": im.get_user_answer('registration_name_last')
            },
            farmer: {
                "actor": "/api/v1/actor/",
                "agents": "",
                "crops": crops,
                "districts": ["/api/v1/district/" + im.get_user_answer('registration_district_confirm') + "/"],
                "hh_id": "",
                "id_number": null,
                "markets": "",
                "participant_type": "",
                "wards": null
            }
        };
        return data;
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
    };

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

    self.clear_summary = function(user) {
        self.set_user_item(user, 'summary', {});
    };

    self.sorted_keys = function(obj, cmp) {
        var keys = [];
        for (var k in obj) {
            keys.push(k);
        }
        keys.sort(cmp);
        return keys;
    };

    self.sms_session_summary = function(im) {
        var summary = self.get_user_item(im.user, 'summary', {});
        var section_names = self.sorted_keys(summary);
        if (section_names.length === 0) {
            return success(false);
        }
        var lines = [];
        for (var k in section_names) {
            var section_name = section_names[k];
            var section = summary[section_name];
            var item_names = self.sorted_keys(section, function (i1, i2) {
                return section[i2] - section[i1];
            });
            var items = item_names.slice(0, 3).map(function (item_name) {
                return item_name + " K" + section[item_name]; });
            lines.push(section_name + ": " + items.join(", "));
        }
        var msg = lines.join("\n");
        self.clear_summary(im.user);
        return self.send_sms(im, msg);
    };

    self.send_sms_first_possible_timeout = function(im) {
        var _ = im.i18n;
        var msg = _.gettext("Your Lima Links USSD session timed out." +
                            " Dial *739*739# to resume.");
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
            if (timeouts == 1) {
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
        var p_farmer = lima_links_api.get_farmer(im.user_addr);
        p_farmer.add_callback(function (farmer) {
            if (farmer === null) {
                return new ChoiceState(
                    "registration_start",
                    function (choice) {
                        return choice.value;
                    },
                    _.gettext("Welcome to LimaLinks.\nIn order to use this system we " +
                        "need to register you with a few short questions."),
                    [new Choice("registration_name_first", _.gettext("Register for LimaLinks"))]
                );
            } else {
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
                               ).fetch(farmer.actor.user.first_name + " " + farmer.actor.user.last_name),
                    choices,
                    _.gettext("Please enter the number of the service.")
                );
            }
        });
        return p_farmer;
    });

    self.add_state(new FreeText(
        "registration_name_first",
        "registration_name_last",
        "Please enter your first name"
    ));

    self.add_state(new FreeText(
        "registration_name_last",
        "registration_gender",
        "Please enter your last name"
    ));

    self.add_state(new ChoiceState(
        'registration_gender',
        'registration_town',
        "What is your gender?",
        [
            new Choice("M", "Male"),
            new Choice("F", "Female")
        ]
    ));

    self.add_state(new FreeText(
        "registration_town",
        "registration_district",
        "What is the town your farm is in?"
    ));

    self.add_state(new FreeText(
        "registration_district",
        "registration_district_confirm",
        "What is the district your farm is in?"
    ));

    self.add_creator('registration_district_confirm', function(state_name, im) {
        var _ = im.i18n;
        // Get the users input if they've made any
        var district = im.get_user_answer('registration_district');

        if (district) {
            // find maps
            var lima_links_api = self.lima_links_api(im);
            var p = lima_links_api.all_districts();
            p.add_callback(function(districts) {
                var matches = self.findInArray(self.extractFieldFromArray(districts, "name"), district);
                if (matches.length === 0) {
                    // No districts similar
                    return new FreeText(
                        "registration_district",
                        "registration_district_confirm",
                        _.gettext("Sorry we could not find a matching district. Please retry entering " +
                            "what district your farm is in:")
                    );
                } else {
                    var choices = [];
                    for (var i=0; i<matches.length; i++){
                        choices[choices.length] = new Choice(districts[matches[i]].id, districts[matches[i]].name);
                    }
                    return new ChoiceState(
                        state_name,
                        "registration_crop",
                        _.gettext("Do you mean:"),
                        choices
                    );
                }
            });
            return p;
        } else {
            // Blank or missing district
            return new FreeText(
                "registration_district",
                "registration_district_confirm",
                _.gettext("What is the district your farm is in?")
            );
        }
    });

    self.add_creator('registration_crop', function(state_name, im) {
        var _ = im.i18n;

        var lima_links_api = self.lima_links_api(im);
        var p = lima_links_api.all_crops();
        p.add_callback(function(crops) {
            var choices = [];
            for (var i=0; i<crops.length; i++){
                choices[choices.length] = new Choice(crops[i].id, crops[i].name);
            }
            return new PaginatedChoiceState(
                state_name,
                function (choice) {
                    // build or add to array of crops they want to claim
                    var curr_crops = self.get_user_item(im.user, "registration_crops", []);
                    curr_crops.push(choice.value);
                    self.set_user_item(im.user, "registration_crops",
                                       curr_crops);
                    return "registration_crop_more";
                },
                _.gettext("What crops do you grow?"),
                choices,
                null,
                null,
                {}
            );
        });
        return p;
    });
    
    self.add_state(new ChoiceState(
        "registration_crop_more",
        function (choice) {
            return choice.value;
        },
        "Would you like to add another crop?",
        [
            new Choice("registration_crop", "Yes"),
            new Choice("registration_end", "No")
        ]
    ));


    self.add_state(new EndState(
        "registration_end",
        "Thank you for registering with LimaLinks!",
        "select_service",
        {
            on_enter: function(){
                // save user
                var lima_links_api = self.lima_links_api(im);
                var data = self.registration_data_collect();
                // Create a user first
                var p = lima_links_api.post_user(data.user);
                var farmer_id;
                p.add_callback(function (user) {
                    // Add the data to the farmer object
                    data.farmer.actor += user.id + "/";
                    return data.farmer;
                });
                p.add_callback(function(farmer){
                    // Make the user a farmer
                    return lima_links_api.post_farmer(farmer);
                });
                p.add_callback(function(farmer){
                    // update vumi go contact
                    farmer_id = farmer.id;
                    return self.get_contact();
                });
                p.add_callback(function(contact){
                    var fields = {
                        "magri_id": JSON.stringify(farmer_id)
                    };
                    return im.api_request('contacts.update_extras', {
                        key: contact.key,
                        fields: fields
                    });
                });
                p.add_callback(function(result){
                    return true;
                });
                return p;
            }
        }
    ));


    self.add_creator("select_crop", function(state_name, im) {
        var _ = im.i18n;
        var lima_links_api = self.lima_links_api(im);
        var p = self.get_contact();
        p.add_callback(function(result){
            return lima_links_api.get_farmer(im.user_addr);
        });
        p.add_callback(function (farmer) {
            var choices = farmer.crops.map(function (crop) {
                return new Choice(crop.id, crop.name);
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
        var next_prev = (markets.length > 1 ?
                         _.gettext("Enter 1 for next market," +
                                     " 2 for previous market.") + "\n"
                         : "");
        var exit = _.gettext("Enter 0 to exit.");
        var footer_text = next_prev + exit;

        function page_changed(page) {
            page = (typeof page !== 'undefined') ? page : booklet.get_current_page(im.user);
            var market_id = markets[page][0];
            var market_name = markets[page][1];
            var p = lima_links_api.price_history(market_id, crop_id, 5);
            p.add_callback(function(prices) {
                var title = _.translate("Prices of %1$s in %2$s:"
                                       ).fetch(crop_name, market_name);
                var unit_ids = [];
                var unit_id;
                for (unit_id in prices) {
                    unit_ids.push(unit_id);
                }
                unit_ids.sort();

                var price_lines = [];
                for (var idx in unit_ids) {
                    unit_id = unit_ids[idx];
                    var unit_info = prices[unit_id];
                    var unit_prices = unit_info.prices;
                    var avg_text;
                    if (unit_prices.length) {
                        var sum = unit_prices.reduce(function (x, y) {
                            return x + y; });
                        avg_text = (sum / unit_prices.length).toFixed(2);
                        self.add_summary_item(im.user, crop_name + ", " + unit_info.unit_name,
                                              market_name, avg_text);
                    }
                    else {
                        avg_text = "-";
                    }
                    price_lines.push("  " + unit_info.unit_name + ": " + avg_text);
                }
                if (!price_lines.length) {
                    price_lines.push("  " + _.gettext("No prices available."));
                }

                var price_text = price_lines.join("\n");
                var text = title + "\n" + price_text + "\n";
                return text;
            });
            return p;
        }

        return new BookletState(state_name, {
            next: "end",
            pages: markets.length,
            page_text: page_changed,
            initial_page: initial_market_idx,
            buttons: {"1": -1, "2": +1, "0": "exit"},
            footer_text: footer_text
        });
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
