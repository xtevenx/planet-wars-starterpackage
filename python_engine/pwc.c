#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "structmember.h"

// Define the Planet class ====================================================

typedef struct {
    PyObject_HEAD int planet_id;
    double x;
    double y;
    int owner;
    int num_ships;
    int growth_rate;
} Planet;

static void Planet_dealloc(Planet *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *Planet_new(PyTypeObject *type, PyObject *args,
                            PyObject *kwds) {
    Planet *self = (Planet *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int Planet_init(Planet *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"planet_id", "x",           "y", "owner",
                             "num_ships", "growth_rate", NULL};

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "|iddiii", kwlist, &self->planet_id, &self->x, &self->y,
            &self->owner, &self->num_ships, &self->growth_rate))
        return -1;

    return 0;
}

static PyMemberDef Planet_members[] = {
    {"planet_id", T_INT, offsetof(Planet, planet_id), 0, "planet id"},
    {"x", T_DOUBLE, offsetof(Planet, x), 0, "x coordinate"},
    {"y", T_DOUBLE, offsetof(Planet, y), 0, "y coordinate"},
    {"owner", T_INT, offsetof(Planet, owner), 0, "owner"},
    {"num_ships", T_INT, offsetof(Planet, num_ships), 0, "number of ships"},
    {"growth_rate", T_INT, offsetof(Planet, growth_rate), 0, "growth rate"},
    {NULL} /* Sentinel */
};

static PyObject *Planet_output_info(Planet *self,
                                    PyObject *Py_UNUSED(ignored)) {
    static char s[64];
    snprintf(s, 64, "%.16f,%.16f,%d,%d,%d", self->x, self->y, self->owner,
             self->num_ships, self->growth_rate);
    return PyUnicode_FromString(s);
}

static PyObject *Planet_output_state(Planet *self,
                                     PyObject *Py_UNUSED(ignored)) {
    static char s[16];
    snprintf(s, 16, "%d.%d", self->owner, self->num_ships);
    return PyUnicode_FromString(s);
}

static PyObject *Planet_game_state(Planet *self, PyObject *args,
                                   PyObject *kwds) {
    static char *kwlist[] = {"invert", NULL};

    int invert = 0;
    PyArg_ParseTupleAndKeywords(args, kwds, "|p", kwlist, &invert);

    int owner =
        self->owner == 0 ? 0 : (invert ? -self->owner + 3 : self->owner);

    static char s[64];
    snprintf(s, 64, "P %.16f %.16f %d %d %d", self->x, self->y, owner,
             self->num_ships, self->growth_rate);
    return PyUnicode_FromString(s);
}

static PyMethodDef Planet_methods[] = {
    {"output_info", (PyCFunction)Planet_output_info, METH_NOARGS,
     "Format full planet information for visualizer"},
    {"output_state", (PyCFunction)Planet_output_state, METH_NOARGS,
     "Format partial planet information for visualizer"},
    {"game_state", (PyCFunction)Planet_game_state, METH_VARARGS | METH_KEYWORDS,
     "Format full planet information for game agents"},
    {NULL} /* Sentinel */
};

static PyTypeObject PlanetType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "pwc.Planet",
    .tp_doc = PyDoc_STR("Planet object"),
    .tp_basicsize = sizeof(Planet),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Planet_new,
    .tp_init = (initproc)Planet_init,
    .tp_dealloc = (destructor)Planet_dealloc,
    .tp_members = Planet_members,
    .tp_methods = Planet_methods,
};

// Define the Fleet class =====================================================

#define FLEET_OUTPUT_STATE_LENGTH 32
#define FLEET_GAME_STATE_LENGTH 32

typedef struct {
    PyObject_HEAD int owner;
    int num_ships;
    int source_planet;
    int destination_planet;
    int total_trip_length;
    int turns_remaining;
    char output_state_string[FLEET_OUTPUT_STATE_LENGTH];
    size_t output_state_length;
    char game_state_string[FLEET_GAME_STATE_LENGTH];
    size_t game_state_length;
} Fleet;

static void Fleet_dealloc(Fleet *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *Fleet_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    Fleet *self = (Fleet *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int Fleet_init(Fleet *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"owner",
                             "num_ships",
                             "source_planet",
                             "destination_planet",
                             "total_trip_length",
                             "turns_remaining",
                             NULL};

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "|iiiiii", kwlist, &self->owner, &self->num_ships,
            &self->source_planet, &self->destination_planet,
            &self->total_trip_length, &self->turns_remaining))
        return -1;

    self->output_state_length = snprintf(
        self->output_state_string, FLEET_OUTPUT_STATE_LENGTH, "%d.%d.%d.%d.%d.",
        self->owner, self->num_ships, self->source_planet,
        self->destination_planet, self->total_trip_length);

    self->game_state_length =
        snprintf(self->game_state_string, FLEET_GAME_STATE_LENGTH,
                 "F ? %d %d %d %d ", self->num_ships, self->source_planet,
                 self->destination_planet, self->total_trip_length);

    return 0;
}

static PyMemberDef Fleet_members[] = {
    {"owner", T_INT, offsetof(Fleet, owner), 0, "owner"},
    {"num_ships", T_INT, offsetof(Fleet, num_ships), 0, "number of ships"},
    {"source_planet", T_INT, offsetof(Fleet, source_planet), 0,
     "source planet"},
    {"destination_planet", T_INT, offsetof(Fleet, destination_planet), 0,
     "destination planet"},
    {"total_trip_length", T_INT, offsetof(Fleet, total_trip_length), 0,
     "total trip length"},
    {"turns_remaining", T_INT, offsetof(Fleet, turns_remaining), 0,
     "turns remaining"},
    {NULL} /* Sentinel */
};

static PyObject *Fleet_output_state(Fleet *self, PyObject *Py_UNUSED(ignored)) {
    snprintf(self->output_state_string + self->output_state_length,
             FLEET_OUTPUT_STATE_LENGTH - self->output_state_length, "%d",
             self->turns_remaining);
    return PyUnicode_FromString(self->output_state_string);
}

static PyObject *Fleet_game_state(Fleet *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"invert", NULL};

    int invert = 0;
    PyArg_ParseTupleAndKeywords(args, kwds, "|p", kwlist, &invert);

    self->game_state_string[2] = self->owner * (1 + invert) % 3 + '0';
    snprintf(self->game_state_string + self->game_state_length,
             FLEET_GAME_STATE_LENGTH - self->game_state_length, "%d",
             self->turns_remaining);
    return PyUnicode_FromString(self->game_state_string);
}

static PyMethodDef Fleet_methods[] = {
    {"output_state", (PyCFunction)Fleet_output_state, METH_NOARGS,
     "Format partial fleet information for visualizer"},
    {"game_state", (PyCFunction)Fleet_game_state, METH_VARARGS | METH_KEYWORDS,
     "Format full fleet information for game agents"},
    {NULL} /* Sentinel */
};

static PyTypeObject FleetType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "pwc.Fleet",
    .tp_doc = PyDoc_STR("Fleet object"),
    .tp_basicsize = sizeof(Fleet),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Fleet_new,
    .tp_init = (initproc)Fleet_init,
    .tp_dealloc = (destructor)Fleet_dealloc,
    .tp_members = Fleet_members,
    .tp_methods = Fleet_methods,
};

// Initialize the module ======================================================

static PyModuleDef pwc_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "pwc",
    .m_doc = "Fast implementation of Planet Wars objects in C.",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_pwc(void) {
    if (PyType_Ready(&PlanetType) < 0)
        return NULL;

    if (PyType_Ready(&FleetType) < 0)
        return NULL;

    PyObject *module = PyModule_Create(&pwc_module);
    if (module == NULL)
        return NULL;

    Py_INCREF(&PlanetType);
    if (PyModule_AddObject(module, "Planet", (PyObject *)&PlanetType) < 0) {
        Py_DECREF(&PlanetType);
        Py_DECREF(module);
        return NULL;
    }

    Py_INCREF(&FleetType);
    if (PyModule_AddObject(module, "Fleet", (PyObject *)&FleetType) < 0) {
        Py_DECREF(&FleetType);
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
