#modules that have tests
TEST_MODULES=neurom
#modules that are installable (ie: ones with setup.py)
INSTALL_MODULES=.
#packages to cover
COVER_PACKAGES=neurom
# documentation to build, separated by spaces
DOC_MODULES=doc

##### DO NOT MODIFY BELOW #####################

ifndef CI_DIR
CI_REPO?=ssh://bbpcode.epfl.ch/platform/ContinuousIntegration.git
CI_DIR?=ContinuousIntegration

FETCH_CI := $(shell \
		if [ ! -d $(CI_DIR) ]; then \
			git clone $(CI_REPO) $(CI_DIR) > /dev/null ;\
		fi;\
		echo $(CI_DIR) )
endif

include $(CI_DIR)/python/common_makefile