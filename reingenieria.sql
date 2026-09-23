-- =====================================================
-- REINGENIERÍA TOTAL - Base de Datos Historial Médico
-- Sin esquemas, todo en public
-- =====================================================

-- =====================================================
-- 1. CREAR TIPOS ENUM
-- =====================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_nombre') THEN
        CREATE TYPE tipo_nombre AS ENUM ('NOMBRE', 'APELLIDO');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sexo') THEN
        CREATE TYPE sexo AS ENUM ('M', 'F', 'OTRO');
    END IF;
END$$;

-- =====================================================
-- 2. CREAR TABLAS
-- =====================================================

-- ---------- identificacion ----------
CREATE TABLE IF NOT EXISTS nombres
(
    id serial NOT NULL,
    tipo tipo_nombre NOT NULL,
    descripcion character varying(30) NOT NULL,
    CONSTRAINT nombres_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS etnia
(
    id serial NOT NULL,
    tipo_etnia character varying(10) NOT NULL,
    CONSTRAINT etnia_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS sangre
(
    id serial NOT NULL,
    tipo_sangre character varying(20) NOT NULL,
    CONSTRAINT sangre_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS direccion
(
    id serial NOT NULL,
    division_politica character varying(50) NOT NULL,
    divicion_politica_id integer,
    valor character varying(100) NOT NULL,
    CONSTRAINT direccion_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS especialidad
(
    id serial NOT NULL,
    descripcion character varying(30) NOT NULL,
    estado boolean NOT NULL DEFAULT true,
    CONSTRAINT especialidad_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS persona
(
    id serial NOT NULL,
    nombre_id integer NOT NULL,
    apellido_id integer NOT NULL,
    fecha_nacimiento date NOT NULL,
    direccion_id integer NOT NULL,
    sexo sexo,
    etnia_id integer,
    sangre_id integer,
    CONSTRAINT persona_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS identificacion
(
    id serial NOT NULL,
    persona_id integer NOT NULL,
    descripcion character varying(50) NOT NULL,
    descripcion_id integer,
    valor character varying(100) NOT NULL,
    CONSTRAINT identificacion_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS medico
(
    id serial NOT NULL,
    persona_id integer NOT NULL,
    especialidad_id integer NOT NULL,
    estado boolean NOT NULL DEFAULT true,
    CONSTRAINT medico_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS paciente
(
    id serial NOT NULL,
    persona_id integer NOT NULL,
    CONSTRAINT paciente_pkey PRIMARY KEY (id)
);

-- ---------- antecedentes_salud ----------
CREATE TABLE IF NOT EXISTS antecedentes_salud
(
    id serial NOT NULL,
    descrip character varying(20) NOT NULL,
    antecedente_salud_id integer NOT NULL,
    valor character varying(20) NOT NULL,
    paciente_id integer NOT NULL,
    CONSTRAINT antecedentes_salud_pkey PRIMARY KEY (id)
);

-- ---------- citas ----------
CREATE TABLE IF NOT EXISTS cita
(
    id serial NOT NULL,
    medico_id integer NOT NULL,
    paciente_id integer NOT NULL,
    fecha_atencion date NOT NULL,
    fecha_creacion time without time zone NOT NULL,
    estado_cita_id integer NOT NULL,
    CONSTRAINT cita_pkey PRIMARY KEY (id)
);

-- ---------- diagnostico ----------
CREATE TABLE IF NOT EXISTS consulta
(
    id serial NOT NULL,
    cita_id integer NOT NULL,
    tipo_consulta integer NOT NULL,
    CONSTRAINT consulta_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS diagnostico
(
    id serial NOT NULL,
    consulta_id integer NOT NULL,
    CONSTRAINT diagnostico_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS enfermedad
(
    id serial NOT NULL,
    "desc" character varying(20)[] NOT NULL,
    valor character varying(20) NOT NULL,
    enfermedad_id integer NOT NULL,
    diagnostico_id integer NOT NULL,
    CONSTRAINT enfermedad_pkey PRIMARY KEY (id, enfermedad_id)
);

CREATE TABLE IF NOT EXISTS sintomas
(
    id serial NOT NULL,
    sintoma character varying(20) NOT NULL,
    diagnostico_id integer NOT NULL,
    CONSTRAINT sintomas_pkey PRIMARY KEY (id)
);

-- ---------- mediciones ----------
CREATE TABLE IF NOT EXISTS equipos
(
    id serial NOT NULL,
    nombre character varying(100) NOT NULL,
    tipo_tecnologia character varying(50) NOT NULL,
    marca character varying(50) NOT NULL,
    modelo character varying(50) NOT NULL,
    CONSTRAINT equipos_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS parametros
(
    id serial NOT NULL,
    dsc character varying(100) NOT NULL,
    dep_id integer,
    dep_dsc character varying(100),
    unidad character varying(20) NOT NULL,
    CONSTRAINT parametros_pkey PRIMARY KEY (id),
    CONSTRAINT parametros_id_dsc_unique UNIQUE (id, dsc)
);

CREATE TABLE IF NOT EXISTS equipo_parametros
(
    id serial NOT NULL,
    equipo_id integer NOT NULL,
    parametro_id integer NOT NULL,
    CONSTRAINT equipo_parametros_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS mediciones_cabecera
(
    id serial NOT NULL,
    fecha_toma timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paciente_id integer NOT NULL,
    CONSTRAINT mediciones_cabecera_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS mediciones_detalles
(
    id serial NOT NULL,
    medicion_id integer NOT NULL,
    equipo_parametro_id integer NOT NULL,
    valor_arrojado numeric(10, 2) NOT NULL,
    CONSTRAINT mediciones_detalles_pkey PRIMARY KEY (id)
);

-- =====================================================
-- 3. CREAR FOREIGN KEYS
-- =====================================================

-- ---------- antecedentes_salud ----------
ALTER TABLE IF EXISTS antecedentes_salud
    ADD CONSTRAINT paciente_fk FOREIGN KEY (paciente_id)
    REFERENCES paciente (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

-- ---------- citas ----------
ALTER TABLE IF EXISTS cita
    ADD CONSTRAINT medico_fk FOREIGN KEY (medico_id)
    REFERENCES medico (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS cita
    ADD CONSTRAINT pa_c_fk FOREIGN KEY (paciente_id)
    REFERENCES paciente (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

-- ---------- diagnostico ----------
ALTER TABLE IF EXISTS diagnostico
    ADD CONSTRAINT consulta_fk FOREIGN KEY (consulta_id)
    REFERENCES consulta (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS enfermedad
    ADD CONSTRAINT diagnostico_fk FOREIGN KEY (diagnostico_id)
    REFERENCES diagnostico (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS sintomas
    ADD CONSTRAINT sintomas_fkey FOREIGN KEY (diagnostico_id)
    REFERENCES diagnostico (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

-- ---------- identificacion ----------
ALTER TABLE IF EXISTS direccion
    ADD CONSTRAINT direccion_divicion_fkey FOREIGN KEY (divicion_politica_id)
    REFERENCES direccion (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS identificacion
    ADD CONSTRAINT identificacion_descripcion_fkey FOREIGN KEY (descripcion_id)
    REFERENCES identificacion (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS identificacion
    ADD CONSTRAINT identificacion_persona_fkey FOREIGN KEY (persona_id)
    REFERENCES persona (id) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE IF EXISTS medico
    ADD CONSTRAINT medico_especialidad_fkey FOREIGN KEY (especialidad_id)
    REFERENCES especialidad (id) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE IF EXISTS medico
    ADD CONSTRAINT medico_persona_fkey FOREIGN KEY (persona_id)
    REFERENCES persona (id) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE IF EXISTS paciente
    ADD CONSTRAINT persona_fkey FOREIGN KEY (persona_id)
    REFERENCES persona (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS persona
    ADD CONSTRAINT persona_apellido_fkey FOREIGN KEY (apellido_id)
    REFERENCES nombres (id) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE IF EXISTS persona
    ADD CONSTRAINT persona_direccion_fkey FOREIGN KEY (direccion_id)
    REFERENCES direccion (id) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE IF EXISTS persona
    ADD CONSTRAINT persona_etnia_fkey FOREIGN KEY (etnia_id)
    REFERENCES etnia (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS persona
    ADD CONSTRAINT persona_nombre_fkey FOREIGN KEY (nombre_id)
    REFERENCES nombres (id) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE IF EXISTS persona
    ADD CONSTRAINT persona_sangre_fkey FOREIGN KEY (sangre_id)
    REFERENCES sangre (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

-- ---------- mediciones ----------
ALTER TABLE IF EXISTS equipo_parametros
    ADD CONSTRAINT equipo_parametros_equipo_fkey FOREIGN KEY (equipo_id)
    REFERENCES equipos (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS equipo_parametros
    ADD CONSTRAINT equipo_parametros_parametro_fkey FOREIGN KEY (parametro_id)
    REFERENCES parametros (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS mediciones_cabecera
    ADD CONSTRAINT paciente_fkey FOREIGN KEY (paciente_id)
    REFERENCES paciente (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS mediciones_detalles
    ADD CONSTRAINT mediciones_detalles_equipo_parametro_fkey FOREIGN KEY (equipo_parametro_id)
    REFERENCES equipo_parametros (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE IF EXISTS mediciones_detalles
    ADD CONSTRAINT mediciones_detalles_medicion_fkey FOREIGN KEY (medicion_id)
    REFERENCES mediciones_cabecera (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE CASCADE;

ALTER TABLE IF EXISTS parametros
    ADD CONSTRAINT parametros_dep_fkey FOREIGN KEY (dep_id, dep_dsc)
    REFERENCES parametros (id, dsc) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION;

-- =====================================================
-- 4. CREAR ÍNDICES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_direccion_divicion
    ON direccion(divicion_politica_id);

CREATE INDEX IF NOT EXISTS idx_identificacion_descripcion
    ON identificacion(descripcion_id);

CREATE INDEX IF NOT EXISTS idx_identificacion_persona
    ON identificacion(persona_id);

CREATE INDEX IF NOT EXISTS idx_medico_especialidad
    ON medico(especialidad_id);

CREATE INDEX IF NOT EXISTS idx_medico_persona
    ON medico(persona_id);

CREATE INDEX IF NOT EXISTS idx_persona_apellido
    ON persona(apellido_id);

CREATE INDEX IF NOT EXISTS idx_persona_direccion
    ON persona(direccion_id);

CREATE INDEX IF NOT EXISTS idx_persona_nombre
    ON persona(nombre_id);

CREATE INDEX IF NOT EXISTS idx_equipo_parametros_equipo
    ON equipo_parametros(equipo_id);

CREATE INDEX IF NOT EXISTS idx_equipo_parametros_parametro
    ON equipo_parametros(parametro_id);

CREATE INDEX IF NOT EXISTS idx_mediciones_detalles_equipo_parametro
    ON mediciones_detalles(equipo_parametro_id);

CREATE INDEX IF NOT EXISTS idx_mediciones_detalles_medicion
    ON mediciones_detalles(medicion_id);
