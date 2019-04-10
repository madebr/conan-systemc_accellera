#include <systemc.h>

template<size_t N>
SC_MODULE(counter) {
    sc_in<bool> clk;
    sc_in<bool> clr;
    sc_out<sc_uint<N> > out;

    int value;

    void count() {
        if (clr) {
            value = 0;
        } else if (clk) {
            value += 1;
        }
        out = value;
    }

    SC_CTOR(counter) {
        SC_METHOD(count);
            sensitive << clr << clk.pos();
            dont_initialize();
    }
};

template<size_t N>
SC_MODULE(counter_test) {
    sc_signal<bool> clk;
    sc_signal<bool> rst;
    sc_signal<sc_uint<N> > cnt;

    sc_trace_file *tf;

    counter<N> dut;

    void stimulus() {
        int i;

        clk.write(1);
        wait(1, SC_NS);
        clk.write(0);
        wait(1, SC_NS);

        rst.write(1);

        for(i = 0; i < 5; ++i) {
            clk.write(1);
            wait(1, SC_NS);
            clk.write(0);
            wait(1, SC_NS);
        }

        rst.write(0);
        for(i = 0; i < 10; ++i) {
            clk.write(1);
            wait(1, SC_NS);
            clk.write(0);
            wait(1, SC_NS);
        }

        rst.write(1);

        for(i = 0; i < 5; ++i) {
            clk.write(1);
            wait(1, SC_NS);
            clk.write(0);
            wait(1, SC_NS);
        }

        rst.write(0);
        for(i = 0; i < 10; ++i) {
            clk.write(1);
            wait(1, SC_NS);
            clk.write(0);
            wait(1, SC_NS);
        }

        clk.write(1);
        wait(1, SC_NS);

        rst.write(1);

        clk.write(0);
        wait(1, SC_NS);

        for(i = 0; i < 5; ++i) {
            clk.write(1);
            wait(1, SC_NS);
            clk.write(0);
            wait(1, SC_NS);
        }

        rst.write(0);
        for(i = 0; i < 10; ++i) {
            clk.write(1);
            wait(1, SC_NS);
            clk.write(0);
            wait(1, SC_NS);
        }
        sc_stop();
    }

    SC_CTOR(counter_test)
        : clk("clock")
        , rst("reset")
        , cnt("count")
        , dut("dut") {
        dut.clk(clk);
        dut.clr(rst);
        dut.out(cnt);

        tf = sc_create_vcd_trace_file("counter");
        sc_trace(tf, clk, "clock");
        sc_trace(tf, rst, "reset");
        sc_trace(tf, cnt, "count");

        SC_THREAD(stimulus);
    }

    ~counter_test() {
        sc_close_vcd_trace_file(tf);
    }
};


int sc_main(int, char **)
{
    sc_set_time_resolution(1, SC_NS);

    counter_test<32> test_bench("counter_test");

    sc_start();

    return 0;
}
