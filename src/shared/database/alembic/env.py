import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, text
from sqlalchemy import pool

from alembic import context
from alembic.runtime.migration import MigrationContext

# Add project root to path (src/shared/database/alembic/ -> project root)
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")),
)

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with environment variable if available
database_url = os.getenv(
    "DATABASE_SYNC_URL", "postgresql+psycopg2://user:password@localhost:5432/job_finder"
)
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and all models for autogenerate support
from src.shared.database.sql_client import Base

# Profile module models
from src.modules.profile.features.user.models import User
from src.modules.profile.features.profile.models import Profile, ProfileSkills
from src.modules.profile.features.link.models import Link, ProfileLink
from src.modules.profile.features.experience.models import (
    Experience,
    Achievements,
    ExperienceSkills,
    ProfileExperience,
)
from src.modules.profile.features.education.models import (
    Education,
    EducationSkills,
    ProfileEducation,
)
from src.modules.profile.features.certificate.models import (
    Certificate,
    CertificateSkills,
    ProfileCertificate,
)
from src.modules.profile.features.company.models import Company
from src.modules.profile.features.skill.models import Skill

# Enterprise module models
from src.modules.enterprise.features.location.models import Location
from src.modules.enterprise.features.segment.models import Segment
from src.modules.enterprise.features.company.models import EnterpriseCompany, CompanyUnit, CompanySegment
from src.modules.enterprise.features.contract.models import Contract
from src.modules.enterprise.features.requirement.models import Requirement
from src.modules.enterprise.features.responsability.models import Responsability
from src.modules.enterprise.features.vacancy.models import Vacancy, VacancyRequirement, VacancyResponsability
from src.modules.enterprise.features.meta.models import Meta

# Set target metadata for autogenerate
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
    )

    with context.begin_transaction():
        if context.get_starting_revision_argument() is None:
            context.execute("CREATE SCHEMA IF NOT EXISTS profile")
            context.execute("CREATE SCHEMA IF NOT EXISTS enterprise")
            context.execute("CREATE SCHEMA IF NOT EXISTS auth")
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Create schemas if they don't exist
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS profile"))
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS enterprise"))
        if MigrationContext.configure(connection).get_current_revision() is None:
            # Historical revisions still create tables in auth on a fresh DB.
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
