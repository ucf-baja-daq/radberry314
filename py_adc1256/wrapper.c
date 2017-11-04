#include <Python.h>
#include "wrapper.h"

// Docstrings
static char module_docstring[] = "This is a python wrapper for the Waveshare AD-DA board.";

// Functions
static PyObject * extend_test(PyObject * self, PyObject * args) {
	int * test_int;
	int ret;

	if (!PyArg_ParseTuple(args, "I", &test_int)) {
		return NULL;
	}

	ret = extendTest(test_int);
	return PyLong_FromLong(ret);
}

static PyObject * start_adc(PyObject * self, PyObject * args);

// Method specification
static PyMethodDef module_methods[] = {
	{"extend_test", extend_test, METH_VARARGS, "Extension test"},
	{"start_adc", start_adc, METH_VARARGS, "Set gain, sampling rate, and scan mode on ads1256 chip."},
	{NULL}
};

// Module specification
static struct PyModuleDef ads1256module = {
    PyModuleDef_HEAD_INIT,
    "ads1256",   /* name of module */
    module_docstring, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    module_methods
};

PyMODINIT_FUNC
PyInit_ads1256(void)
{
    return PyModule_Create(&ads1256module);
}

static PyObject * start_adc(PyObject * self, PyObject * args) {
	int * gain, * sampling_rate, * scan_mode;
	int returnValue;

	// parse arguments as long integers
	if (!PyArg_ParseTuple(args, "I", &gain, &sampling_rate, &scan_mode)) {
		return NULL;
	}

	// run startADC()
	returnValue = startADC(gain, sampling_rate, scan_mode);

	// dummy return for python object
	return PyLong_FromLong(returnValue);
}
