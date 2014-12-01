
typedef struct pypy_defs {
   void (*setup_numpy_data)(int[]);
   void (*clean_namespace)();
   void* (* basic_register)(char *, char *, char *, char *);
   void (*extra_source)(char *);
   char *last_exception;
} pypy_defs;
