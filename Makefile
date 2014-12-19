PAGE_EVALUATOR_VERSION := 1.0.0
PAGE_CORRECTOR_VERSION := 1.8.0
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SRC_DIR := $(ROOT_DIR)/src
LIB_DIR := $(ROOT_DIR)/lib
SEASR_HOME ?= $(LIB_DIR)/seasr
JUXTA_HOME ?= $(LIB_DIR)/juxta-cl
RETAS_HOME ?= $(LIB_DIR)/retas

_default: all

all: build install

build: build_seasr build_juxta_cl build_retas

build_seasr:
	mvn -f $(SRC_DIR)/seasr/PageEvaluator package
	mvn -f $(SRC_DIR)/seasr/PageCorrector package

build_juxta_cl:
	mvn -f $(SRC_DIR)/Juxta-cl package

build_retas:
	cd $(SRC_DIR)/RETAS && javac *.java

install: build install_seasr install_juxta_cl install_retas

install_seasr:
	install -d $(LIB_DIR)/seasr
	install -m 0664 $(SRC_DIR)/seasr/PageEvaluator/target/PageEvaluator-$(PAGE_EVALUATOR_VERSION)-SNAPSHOT.jar $(SEASR_HOME)/PageEvaluator.jar
	install -m 0664 $(SRC_DIR)/seasr/PageCorrector/target/PageCorrector-$(PAGE_CORRECTOR_VERSION)-SNAPSHOT.jar $(SEASR_HOME)/PageCorrector.jar

install_juxta_cl:
	install -d $(JUXTA_HOME)
	install -d $(JUXTA_HOME)/lib
	install -m 0664 $(SRC_DIR)/Juxta-cl/target/juxta-cl.jar $(JUXTA_HOME)/juxta-cl.jar
	install $(SRC_DIR)/Juxta-cl/scripts/*.sh $(JUXTA_HOME)/
	install -m 0664 $(SRC_DIR)/Juxta-cl/target/lib/*.jar $(JUXTA_HOME)/lib/

install_retas:
	install -d $(RETAS_HOME)
	jar cf $(RETAS_HOME)/retas.jar $(SRC_DIR)/RETAS/*.class
	install -m 0664 $(SRC_DIR)/RETAS/config.txt $(RETAS_HOME)/config.txt

clean: clean_seasr clean_juxta_cl clean_retas

clean_seasr:
	rm -r $(SRC_DIR)/seasr/PageCorrector/target/*
	rm -r $(SRC_DIR)/seasr/PageEvaluator/target/*

clean_juxta_cl:
	rm -r $(SRC_DIR)/Juxta-cl/target/*

clean_retas:
	rm $(SRC_DIR)/RETAS/*.class

uninstall: uninstall_seasr uninstall_juxta_cl uninstall_retas

uninstall_seasr:
	rm $(SEASR_HOME)/PageEvaluator.jar
	rm $(SEASR_HOME)/PageCorrector.jar

uninstall_juxta_cl:
	rm $(JUXTA_HOME)/juxta-cl.jar
	rm $(JUXTA_HOME)/*.sh
	rm $(JUXTA_HOME)/lib/*.jar

uninstall_retas:
	rm $(RETAS_HOME)/retas.jar
	rm $(RETAS_HOME)/config.txt
