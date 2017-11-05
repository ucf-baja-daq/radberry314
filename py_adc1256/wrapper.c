#include <Python.h>
#include "wrapper.h"

// Docstrings
static char module_docstring[] = "This is a python wrapper for the Waveshare AD-DA board.";

// Functions
static PyObject * startADC(PyObject * self, PyObject * args);
static PyObject * stopADC(PyObject * self, PyObject * args);

// Method specification
static PyMethodDef module_methods[] = {
	{"startADC", startADC, METH_VARARGS, "Set gain, sampling rate, and scan mode on ads1256 chip."},
	{"stopADC", stopADC, METH_VARARGS, "End spi interface."},
	{NULL, NULL, 0, NULL}
};

// Module specification
static struct PyModuleDef pyadda_module = {
    PyModuleDef_HEAD_INIT,
    "pyadda",   /* name of module */
    module_docstring, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    module_methods
};

PyMODINIT_FUNC PyInit_pyadda(void) {
    return PyModule_Create(&pyadda_module);
}

static PyObject * startADC(PyObject * self, PyObject * args) {
	int gain, sampling_rate, scan_mode;

	// parse arguments as long integers
	if (!PyArg_ParseTuple(args, "III", &gain, &sampling_rate, &scan_mode)) {
		return NULL;
	}

	// run startADC()
	int value = start_ADC(gain, sampling_rate, scan_mode);

	// build the output tuple
	PyObject * ret = Py_BuildValue("i",value);
    return ret;
}

static PyObject * stopADC(PyObject * self, PyObject * args) {
	// run startADC()
	int value = stop_ADC();

	// build the output tuple
	PyObject * ret = Py_BuildValue("i",value);
    return ret;
}
