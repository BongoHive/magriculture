// Tests for magri-ussd.js

var assert = require("assert");
var vumigo = require("vumigo_v01");
var app = require("../lib/magri-ussd");
var test_utils = vumigo.test_utils;


// This just checks that you hooked you InteractionMachine
// up to the api correctly and called im.attach();
describe("test_api", function() {
    it("should exist", function() {
        assert.ok(app.api);
    });
    it("should have an on_inbound_message method", function() {
        assert.ok(app.api.on_inbound_message);
    });
    it("should have an on_inbound_event method", function() {
        assert.ok(app.api.on_inbound_event);
    });
});

var tester;

var test_fixtures_full = [
    "test/fixtures/farmer.json",
    "test/fixtures/highest_markets.json",
    "test/fixtures/markets.json",
    "test/fixtures/markets_1.json",
    "test/fixtures/price_history.json",
    "test/fixtures/price_history_market2.json",
    "test/fixtures/price_history_none.json",
    "test/fixtures/district.json",
    "test/fixtures/crop.json",
];

var test_fixtures_registration = [
    "test/fixtures/farmer_404.json",
    "test/fixtures/district.json",
    "test/fixtures/crop.json",
    "test/fixtures/farmer_post.json",
    "test/fixtures/user_post.json",
];


describe("as an unregistered farmer", function() {

    var fixtures = test_fixtures_registration;
    beforeEach(function() {
        tester = new vumigo.test_utils.ImTester(app.api, {
            custom_setup: function (api) {
                api.config_store.config = JSON.stringify({
                    lima_links_api: {
                        url: "http://qa/api/v1/",
                        username: "test",
                        password: "password",
                    }
                });

                var dummy_contact = {
                    key: "f953710a2472447591bd59e906dc2c26",
                    surname: "Trotter",
                    user_account: "test-0-user",
                    bbm_pin: null,
                    msisdn: +1111111,
                    created_at: "2013-04-24 14:01:41.803693",
                    gtalk_id: null,
                    dob: null,
                    groups: null,
                    facebook_id: null,
                    twitter_handle: null,
                    email_address: null,
                    name: "Rodney"
                };

                api.add_contact(dummy_contact);

                fixtures.forEach(function (f) {
                    api.load_http_fixture(f);
                });
            },
            async: true
        });
    });

    var assert_summary_equal = function(summary) {
        function teardown(api, saved_user) {
            assert.deepEqual(saved_user.custom.summary, summary);
        }
        return teardown;
    };

    it("I should be asked to register", function (done) {
        var p = tester.check_state({
            user: null,
            content: null,
            next_state: "registration_start",
            response: "^Welcome to LimaLinks.[^]" +
                "In order to use this system we need to register you with a few short questions.[^]" +
                "1. Register for LimaLinks$"
        });
        p.then(done, done);
    });

    it("I should be asked for first name", function (done) {
        var p = tester.check_state({
            user: {current_state: "registration_start"},
            content: "1",
            next_state: "registration_name_first",
            response: "^Please enter your first name$"
        });
        p.then(done, done);
    });


    it("Entering first name I should be asked for last name", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_name_first",
                answers: {
                    registration_start: "registration_name_first"
                }
            },
            content: "Bob",
            next_state: "registration_name_last",
            response: "^Please enter your last name$"
        });
        p.then(done, done);
    });

    it("Entering last name I should be asked for gender", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_name_last",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob"
                }
            },
            content: "Marley",
            next_state: "registration_gender",
            response: "^What is your gender\\?[^]" +
            "1. Male[^]" +
            "2. Female$"
        });
        p.then(done, done);
    });

    it("Entering gender I should be asked for location", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_gender",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley"
                }
            },
            content: "1",
            next_state: "registration_town",
            response: "^What is the town your farm is in\\?$"
        });
        p.then(done, done);
    });

    it("Entering town I should be asked for district", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_town",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M"
                }
            },
            content: "Choma",
            next_state: "registration_district",
            response: "^What is the district your farm is in\\?$"
        });
        p.then(done, done);
    });

    it("Entering bad district I should be asked for district again", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_district",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_town: "town one"
                }
            },
            content: "four",
            next_state: "registration_district",
            response: "^Sorry we could not find a matching district. Please retry entering " +
                            "what district your farm is in:$"
        });
        p.then(done, done);
    });

    it("Entering good district I should be asked for confirmation", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_district",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_town: "town one"
                }
            },
            content: "three",
            next_state: "registration_district_confirm",
            response: "^Do you mean:[^]" +
                        "1. district three$"
        });
        p.then(done, done);
    });

    it("Entering good district but not unique district I should be asked for confirmation", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_district",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_town: "town one"
                }
            },
            content: "district",
            next_state: "registration_district_confirm",
            response: "^Do you mean:[^]" +
                        "1. district one[^]" +
                        "2. district two[^]" +
                        "3. district three$"
        });
        p.then(done, done);
    });

    it("Confirming district I should be asked for crop", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_district_confirm",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_town: "town one",
                    registration_district: "one"
                }
            },
            content: "1",
            next_state: "registration_crop",
            response: "^What crops do you grow\\?[^]" +
                        "1. Beans[^]" +
                        "2. Cabbage[^]" +
                        "3. Carrots[^]" +
                        "4. Cassava[^]" +
                        "5. Cauliflower[^]" +
                        "6. Chinese Cabbage[^]" +
                        "7. Coffee[^]" +
                        "8. Eggplant[^]" +
                        "9. More$"
        });
        p.then(done, done);
    });

    it("Choosing more option on crop should show more", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_crop",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_town: "town one",
                    registration_district: "one"
                }
            },
            content: "9",
            next_state: "registration_crop",
            response: "^What crops do you grow\\?[^]" +
                        "1. Fruit[^]" +
                        "2. Green Maize[^]" +
                        "3. Green Pepper[^]" +
                        "4. Impwa[^]" +
                        "5. Kalembula[^]" +
                        "6. Maize[^]" +
                        "7. Millet[^]" +
                        "8. Okra[^]" +
                        "9. More[^]" +
                        "10. Back$"
        });
        p.then(done, done);
    });

    it("Choosing more again option on crop should show more again", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_crop",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_town: "town one",
                    registration_district: "one"
                },
                pages: {
                    registration_crop: 8
                }
            },
            content: "9",
            next_state: "registration_crop",
            response: "^What crops do you grow\\?[^]" +
                        "1. Onion[^]" +
                        "2. Pumpkin Leaves[^]" +
                        "3. Rape[^]" +
                        "4. Rice[^]" +
                        "5. Soybean[^]" +
                        "6. Sugar Cane[^]" +
                        "7. Sunflowers[^]" +
                        "8. Tobacco[^]" +
                        "9. More[^]" +
                        "10. Back$"
        });
        p.then(done, done);
    });

    it("Choosing more again option for the third time on crop should show more again", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_crop",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_town: "town one",
                    registration_district: "one"
                },
                pages: {
                    registration_crop: 16
                }
            },
            content: "9",
            next_state: "registration_crop",
            response: "^What crops do you grow\\?[^]" +
                        "1. Tomato[^]" +
                        "2. Wheat[^]" +
                        "3. Fruit - Oranges[^]" +
                        "4. Fruit - Apples[^]" +
                        "5. Fruit - Bananas[^]" +
                        "6. Back$"
        });
        p.then(done, done);
    });

    it.skip("Confirming district I should be thanked and exit", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_district_confirm",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_town: "town one",
                    registration_district: "one"
                }
            },
            content: "1",
            next_state: "registration_end",
            response: "^Thank you for registering with LimaLinks!$",
            continue_session: false
        });
        p.then(done, done);
    });


});


describe("test menu worker", function() {

    var fixtures = test_fixtures_full;
    beforeEach(function() {
        tester = new vumigo.test_utils.ImTester(app.api, {
            custom_setup: function (api) {
                api.config_store.config = JSON.stringify({
                    lima_links_api: {
                        url: "http://qa/api/v1/",
                        username: "test",
                        password: "password",
                    }
                });

                var dummy_contact = {
                    key: "f953710a2472447591bd59e906dc2c26",
                    surname: "Trotter",
                    user_account: "test-0-user",
                    bbm_pin: null,
                    msisdn: "+1234567",
                    created_at: "2013-04-24 14:01:41.803693",
                    gtalk_id: null,
                    dob: null,
                    groups: null,
                    facebook_id: null,
                    twitter_handle: null,
                    email_address: null,
                    name: "Rodney"
                };

                api.add_contact(dummy_contact);
                api.update_contact_extras(dummy_contact, {
                    magri_id: 2
                });

                fixtures.forEach(function (f) {
                    api.load_http_fixture(f);
                });
            },
            async: true
        });
    });

    var assert_summary_equal = function(summary) {
        function teardown(api, saved_user) {
            assert.deepEqual(saved_user.custom.summary, summary);
        }
        return teardown;
    };

    it("select_service state should respond", function(done) {
        var p = tester.check_state({
            user: {current_state: "select_service"},
            content: null,
            next_state: "select_service",
            response: ("^Hi Farmer Bob.[^]" +
                       "Select a service:[^]" +
                       "1. Market prices$")
        });
        p.then(done, done);
    });
    it("select_crop should respond", function(done) {
        var p = tester.check_state({
            user: {current_state: "select_crop"},
            content: null,
            next_state: "select_crop",
            response: ("^Select a crop:[^]" +
                       "1. Beans[^]" +
                       "2. Cabbage[^]" +
                       "3. Carrots$")
        });
        p.then(done, done);
    });
    it("select_market_list should respond", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market_list",
                custom: {
                    chosen_crop_name: "Peas"
                }
            },
            content: null,
            next_state: "select_market_list",
            response: ("^Select which markets to view:[^]" +
                       "1. All markets[^]" +
                       "2. Best markets for Peas$")
        });
        p.then(done, done);
    });
    it("select_market should respond (best_markets)", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_crop: "crop1",
                    select_market_list: "best_markets"
                }
            },
            content: null,
            next_state: "select_market",
            response: ("^Select a market:[^]" +
                       "1. Kitwe[^]" +
                       "2. Ndola$")
        });
        p.then(done, done);
    });
    it("select_market should respond (all_markets)", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_market_list: "all_markets"
                }
            },
            content: null,
            next_state: "select_market",
            response: ("^Select a market:[^]" +
                       "1. Kitwe[^]" +
                       "2. Ndola[^]" +
                       "3. Masala$")
        });
        p.then(done, done);
    });
    it("select_market should show_prices for selected market", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_crop: "crop1"
                },
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_crop_name: "Peas"
                }
            },
            content: "1",
            next_state: "show_prices",
            response: ("^Prices of Peas in Kitwe:[^]" +
                       "  boxes: 1.27[^]" +
                       "  crates: 1.70[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to exit\\.$"),
            teardown: assert_summary_equal({
                "Peas, boxes": { "Kitwe": "1.27" },
                "Peas, crates": { "Kitwe": "1.70" }
            })
        });
        p.then(done, done);
    });
    it("select_market should explain if selected market has no prices", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_crop: "crop2"
                },
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_crop_name: "Carrots"
                }
            },
            content: "1",
            next_state: "show_prices",
            response: ("^Prices of Carrots in Kitwe:[^]" +
                       "  No prices available\\.[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to exit\\.$"),
            teardown: assert_summary_equal(undefined)
        });
        p.then(done, done);
    });
    it("show_prices should move to previous market on 1", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "show_prices",
                answers: {
                    select_crop: "crop1"
                },
                pages: {
                    show_prices: 0
                },
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_market_idx: 0,
                    chosen_crop_name: "Peas"
                }
            },
            content: "1",
            next_state: "show_prices",
            response: ("^Prices of Peas in Ndola:[^]" +
                       "  boxes: -[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to exit\\.$")
        });
        p.then(done, done);
    });
    it("show_prices should move to next market on 2", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "show_prices",
                answers: {
                    select_crop: "crop1"
                },
                pages: {
                    show_prices: 1
                },
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_market_idx: 0,
                    chosen_crop_name: "Peas"
                }
            },
            content: "2",
            next_state: "show_prices",
            response: ("^Prices of Peas in Kitwe:[^]" +
                       "  boxes: 1.27[^]" +
                       "  crates: 1.70[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to exit\\.$")
        });
        p.then(done, done);
    });
    it("show_prices should move to end on 0", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "show_prices",
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_market_idx: 0,
                    chosen_crop_name: "Peas"
               }
            },
            content: "0",
            next_state: "end",
            continue_session: false,
            response: ("^Goodbye!")
        });
        p.then(done, done);
    });
});

describe("test sms sending", function() {
    var fixtures = test_fixtures_full;
    beforeEach(function() {
        tester = new vumigo.test_utils.ImTester(app.api, {
            custom_setup: function (api) {
                api.config_store.config = JSON.stringify({
                    sms_tag: ["pool", "tag123"],
                    lima_links_api: {
                        url: "http://qa/api/v1/",
                        username: "test",
                        password: "password",
                    }
                });

                var dummy_contact = {
                    key: "f953710a2472447591bd59e906dc2c26",
                    surname: "Trotter",
                    user_account: "test-0-user",
                    bbm_pin: null,
                    msisdn: "+1234567",
                    created_at: "2013-04-24 14:01:41.803693",
                    gtalk_id: null,
                    dob: null,
                    groups: null,
                    facebook_id: null,
                    twitter_handle: null,
                    email_address: null,
                    name: "Rodney"
                };

                api.add_contact(dummy_contact);

                fixtures.forEach(function (f) {
                    api.load_http_fixture(f);
                });
            },
            custom_teardown: function (api) {
                assert.ok(api.outbound_sends.every(
                    function (send) {
                        return (send.tagpool == "pool" &&
                                send.tag == "tag123" &&
                                send.to_addr == "1234567");
                    }
                ));
            },
            async: true
        });
    });

    var assert_single_sms = function(content) {
        var teardown = function(api) {
            var sms = api.outbound_sends[0];
            assert.equal(api.outbound_sends.length, 1);
            assert.equal(sms.content, content);
        };
        return teardown;
    };

    var assert_no_sms = function() {
        var teardown = function(api) {
            assert.equal(api.outbound_sends.length, 0);
        };
        return teardown;
    };

    var get_user = function() {
        return {
            current_state: "show_prices",
            custom: {
                chosen_markets: [
                    ["market1", "Kitwe"],
                    ["market2", "Ndola"]
                ],
                chosen_market_idx: 0,
                chosen_crop_name: "Peas"
            }
        };
    };

    it("should not sms summary if no prices present", function (done) {
        var p = tester.check_state({
            user: get_user(),
            content: "0",
            next_state: "end",
            continue_session: false,
            response: ("^Goodbye!"),
            teardown: assert_no_sms()
        });
        p.then(done, done);
    });

    it("should sms summary if prices present", function (done) {
        var user = get_user();
        user.custom.summary = {
            "Peas, boxes": {
                "Kitwe": "15000",
                "Ndola": "15500"
            },
            "Peas, crates": {
                "Kitwe": "16000"
            }
        };
        var p = tester.check_state({
            user: user,
            content: "0",
            next_state: "end",
            continue_session: false,
            response: ("^Goodbye!"),
            teardown: assert_single_sms(
                "Peas, boxes: Ndola K15500, Kitwe K15000\n" +
                "Peas, crates: Kitwe K16000"
            )
        });
        p.then(done, done);
    });
});
