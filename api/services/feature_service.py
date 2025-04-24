from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from configs import dify_config
from services.billing_service import BillingService
from services.enterprise.enterprise_service import EnterpriseService


class SubscriptionModel(BaseModel):
    plan: str = "sandbox"
    interval: str = ""


class BillingModel(BaseModel):
    enabled: bool = False
    subscription: SubscriptionModel = SubscriptionModel()


class EducationModel(BaseModel):
    enabled: bool = False
    activated: bool = False


class LimitationModel(BaseModel):
    size: int = 0
    limit: int = 0


class LicenseStatus(StrEnum):
    NONE = "none"
    INACTIVE = "inactive"
    ACTIVE = "active"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    LOST = "lost"


class LicenseModel(BaseModel):
    status: LicenseStatus = LicenseStatus.NONE
    expired_at: str = ""


class FeatureModel(BaseModel):
    billing: BillingModel = BillingModel()
    education: EducationModel = EducationModel()
    members: LimitationModel = LimitationModel(size=0, limit=1)
    apps: LimitationModel = LimitationModel(size=0, limit=10)
    vector_space: LimitationModel = LimitationModel(size=0, limit=5)
    knowledge_rate_limit: int = 1000
    annotation_quota_limit: LimitationModel = LimitationModel(size=0, limit=10)
    documents_upload_quota: LimitationModel = LimitationModel(size=0, limit=50)
    docs_processing: str = "standard"
    can_replace_logo: bool = True
    model_load_balancing_enabled: bool = True
    dataset_operator_enabled: bool = True

    # pydantic configs
    model_config = ConfigDict(protected_namespaces=())


class KnowledgeRateLimitModel(BaseModel):
    enabled: bool = False
    limit: int = 10
    subscription_plan: str = ""


class SystemFeatureModel(BaseModel):
    sso_enforced_for_signin: bool = False
    sso_enforced_for_signin_protocol: str = ""
    sso_enforced_for_web: bool = False
    sso_enforced_for_web_protocol: str = ""
    enable_web_sso_switch_component: bool = False
    enable_marketplace: bool = True
    max_plugin_package_size: int = dify_config.PLUGIN_MAX_PACKAGE_SIZE
    enable_email_code_login: bool = False
    enable_email_password_login: bool = True
    enable_social_oauth_login: bool = False
    is_allow_register: bool = False
    is_allow_create_workspace: bool = True
    is_email_setup: bool = False
    license: LicenseModel = LicenseModel()


class FeatureService:
    @classmethod
    def get_features(cls, tenant_id: str) -> FeatureModel:
        features = FeatureModel()

        cls._fulfill_params_from_env(features)

        if dify_config.BILLING_ENABLED and tenant_id:
            cls._fulfill_params_from_billing_api(features, tenant_id)

        return features

    @classmethod
    def get_knowledge_rate_limit(cls, tenant_id: str):
        knowledge_rate_limit = KnowledgeRateLimitModel()
        if dify_config.BILLING_ENABLED and tenant_id:
            knowledge_rate_limit.enabled = True
            limit_info = BillingService.get_knowledge_rate_limit(tenant_id)
            knowledge_rate_limit.limit = limit_info.get("limit", 10)
            knowledge_rate_limit.subscription_plan = limit_info.get("subscription_plan", "sandbox")
        return knowledge_rate_limit

    @classmethod
    def get_system_features(cls) -> SystemFeatureModel:
        system_features = SystemFeatureModel()

        cls._fulfill_system_params_from_env(system_features)

        if dify_config.ENTERPRISE_ENABLED:
            system_features.enable_web_sso_switch_component = True

            cls._fulfill_params_from_enterprise(system_features)

        return system_features

    @classmethod
    def _fulfill_system_params_from_env(cls, system_features: SystemFeatureModel):
        system_features.enable_email_code_login = dify_config.ENABLE_EMAIL_CODE_LOGIN
        system_features.enable_email_password_login = dify_config.ENABLE_EMAIL_PASSWORD_LOGIN
        system_features.enable_social_oauth_login = dify_config.ENABLE_SOCIAL_OAUTH_LOGIN
        system_features.is_allow_register = dify_config.ALLOW_REGISTER
        system_features.is_email_setup = dify_config.MAIL_TYPE is not None and dify_config.MAIL_TYPE != ""

    @classmethod
    def _fulfill_params_from_env(cls, features: FeatureModel):
        features.education.enabled = dify_config.EDUCATION_ENABLED

    @classmethod
    def _fulfill_params_from_billing_api(cls, features: FeatureModel, tenant_id: str):
        billing_info = BillingService.get_info(tenant_id)

        features.billing.enabled = billing_info["enabled"]
        features.billing.subscription.plan = billing_info["subscription"]["plan"]
        features.billing.subscription.interval = billing_info["subscription"]["interval"]
        features.education.activated = billing_info["subscription"].get("education", False)

        if "members" in billing_info:
            features.members.size = billing_info["members"]["size"]
            features.members.limit = billing_info["members"]["limit"]

        if "apps" in billing_info:
            features.apps.size = billing_info["apps"]["size"]
            features.apps.limit = billing_info["apps"]["limit"]

        if "vector_space" in billing_info:
            features.vector_space.size = billing_info["vector_space"]["size"]
            features.vector_space.limit = billing_info["vector_space"]["limit"]

        if "documents_upload_quota" in billing_info:
            features.documents_upload_quota.size = billing_info["documents_upload_quota"]["size"]
            features.documents_upload_quota.limit = billing_info["documents_upload_quota"]["limit"]

        if "annotation_quota_limit" in billing_info:
            features.annotation_quota_limit.size = billing_info["annotation_quota_limit"]["size"]
            features.annotation_quota_limit.limit = billing_info["annotation_quota_limit"]["limit"]

        if "docs_processing" in billing_info:
            features.docs_processing = billing_info["docs_processing"]

    @classmethod
    def _fulfill_params_from_enterprise(cls, features):
        enterprise_info = EnterpriseService.get_info()

        if "sso_enforced_for_signin" in enterprise_info:
            features.sso_enforced_for_signin = enterprise_info["sso_enforced_for_signin"]

        if "sso_enforced_for_signin_protocol" in enterprise_info:
            features.sso_enforced_for_signin_protocol = enterprise_info["sso_enforced_for_signin_protocol"]

        if "sso_enforced_for_web" in enterprise_info:
            features.sso_enforced_for_web = enterprise_info["sso_enforced_for_web"]

        if "sso_enforced_for_web_protocol" in enterprise_info:
            features.sso_enforced_for_web_protocol = enterprise_info["sso_enforced_for_web_protocol"]

        if "enable_email_code_login" in enterprise_info:
            features.enable_email_code_login = enterprise_info["enable_email_code_login"]

        if "enable_email_password_login" in enterprise_info:
            features.enable_email_password_login = enterprise_info["enable_email_password_login"]

        if "license" in enterprise_info:
            license_info = enterprise_info["license"]

            if "status" in license_info:
                features.license.status = LicenseStatus(license_info.get("status", LicenseStatus.INACTIVE))

            if "expired_at" in license_info:
                features.license.expired_at = license_info["expired_at"]
