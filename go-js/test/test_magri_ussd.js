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
];

describe("test menu worker", function() {

    var fixtures = test_fixtures_full;
    beforeEach(function() {
        tester = new vumigo.test_utils.ImTester(app.api, {
            custom_setup: function (api) {
                api.config_store.config = JSON.stringify({
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
            async: true
        });
    });

    var assert_summary_equal = function(summary) {
        function teardown(api, saved_user) {
            assert.deepEqual(saved_user.custom.summary, summary);
        }
        return teardown;
    };

    it("new users should see the select_service state", function (done) {
        var p = tester.check_state({
            user: null,
            content: null,
            next_state: "select_service",
            response: "^Hi Farmer Bob."
        });
        p.then(done, done);
    });
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
                       "1. Peas[^]" +
                       "2. Carrots$")
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
                    sms_tag: ["pool", "tag123"]
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
