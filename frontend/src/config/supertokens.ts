
import SuperTokens from 'supertokens-auth-react';
import EmailPassword from 'supertokens-auth-react/recipe/emailpassword';
import Session from 'supertokens-auth-react/recipe/session';
import { API_URL } from './api';

SuperTokens.init({
  appInfo: {
    appName: 'AutoGest',
    apiDomain: API_URL,
    websiteDomain: window.location.origin,
    apiBasePath: '/auth',
    websiteBasePath: '/auth',
  },

  // Usamos los formularios oficiales de SuperTokens.
  // El diseño se adapta a la identidad visual de AutoGest.
  useShadowDom: false,

  style: `
    [data-supertokens="container"] {
      font-family: 'Public Sans Variable', sans-serif;
      --palette-primary: 27, 104, 81;
      --palette-primaryBorder: 27, 104, 81;
      --palette-textTitle: 18, 39, 58;
    }

    [data-supertokens="headerTitle"] {
      font-family: 'Fraunces Variable', Georgia, serif;
    }

    [data-supertokens="button"] {
      border-radius: 8px;
      font-family: 'Public Sans Variable', sans-serif;
      font-weight: 600;
    }
  `,

  languageTranslations: {
    defaultLanguage: 'es',

    translations: {
      es: {
        // ========================================
        // ENCABEZADOS GENERALES
        // ========================================

        AUTH_PAGE_HEADER_TITLE_SIGN_IN:
          'Bienvenido de nuevo',

        AUTH_PAGE_HEADER_SUBTITLE_SIGN_IN_START:
          '¿Aún no tienes una cuenta? ',

        AUTH_PAGE_HEADER_SUBTITLE_SIGN_IN_SIGN_UP_LINK:
          'Regístrate',

        AUTH_PAGE_HEADER_SUBTITLE_SIGN_IN_END:
          '',

        AUTH_PAGE_HEADER_TITLE_SIGN_UP:
          'Crea tu cuenta',

        AUTH_PAGE_HEADER_SUBTITLE_SIGN_UP_START:
          '¿Ya tienes una cuenta? ',

        AUTH_PAGE_HEADER_SUBTITLE_SIGN_UP_SIGN_IN_LINK:
          'Inicia sesión',

        AUTH_PAGE_HEADER_SUBTITLE_SIGN_UP_END:
          '',

        // ========================================
        // ETIQUETAS Y CAMPOS COMPARTIDOS
        // ========================================

        EMAIL_PASSWORD_EMAIL_LABEL:
          'Correo electrónico',

        EMAIL_PASSWORD_EMAIL_PLACEHOLDER:
          'tu@correo.com',

        EMAIL_PASSWORD_PASSWORD_LABEL:
          'Contraseña',

        EMAIL_PASSWORD_PASSWORD_PLACEHOLDER:
          'Tu contraseña',

        // ========================================
        // INICIO DE SESIÓN
        // ========================================

        EMAIL_PASSWORD_SIGN_IN_HEADER_TITLE:
          'Bienvenido de nuevo',

        EMAIL_PASSWORD_SIGN_IN_HEADER_SUBTITLE_START:
          '¿Aún no tienes una cuenta? ',

        EMAIL_PASSWORD_SIGN_IN_HEADER_SUBTITLE_SIGN_UP_LINK:
          'Regístrate',

        EMAIL_PASSWORD_SIGN_IN_HEADER_SUBTITLE_END:
          '',

        EMAIL_PASSWORD_SIGN_IN_EMAIL_LABEL:
          'Correo electrónico',

        EMAIL_PASSWORD_SIGN_IN_EMAIL_PLACEHOLDER:
          'tu@correo.com',

        EMAIL_PASSWORD_SIGN_IN_PASSWORD_LABEL:
          'Contraseña',

        EMAIL_PASSWORD_SIGN_IN_PASSWORD_PLACEHOLDER:
          'Tu contraseña',

        EMAIL_PASSWORD_SIGN_IN_SUBMIT_BTN:
          'Iniciar sesión',

        EMAIL_PASSWORD_SIGN_IN_FORGOT_PW_LINK:
          '¿Olvidaste tu contraseña?',

        EMAIL_PASSWORD_SIGN_IN_WRONG_CREDENTIALS_ERROR:
          'Correo electrónico o contraseña incorrectos.',

        // ========================================
        // REGISTRO DE USUARIOS
        // ========================================

        EMAIL_PASSWORD_SIGN_UP_HEADER_TITLE:
          'Crea tu cuenta',

        EMAIL_PASSWORD_SIGN_UP_HEADER_SUBTITLE_START:
          '¿Ya tienes una cuenta? ',

        EMAIL_PASSWORD_SIGN_UP_HEADER_SUBTITLE_SIGN_IN_LINK:
          'Inicia sesión',

        EMAIL_PASSWORD_SIGN_UP_HEADER_SUBTITLE_END:
          '',

        EMAIL_PASSWORD_SIGN_UP_EMAIL_LABEL:
          'Correo electrónico',

        EMAIL_PASSWORD_SIGN_UP_EMAIL_PLACEHOLDER:
          'tu@correo.com',

        EMAIL_PASSWORD_SIGN_UP_PASSWORD_LABEL:
          'Contraseña',

        EMAIL_PASSWORD_SIGN_UP_PASSWORD_PLACEHOLDER:
          'Crea una contraseña segura',

        EMAIL_PASSWORD_SIGN_UP_SUBMIT_BTN:
          'Registrarme',

        EMAIL_PASSWORD_EMAIL_ALREADY_EXISTS:
          'Este correo electrónico ya está registrado.',

        // ========================================
        // RECUPERACIÓN DE CONTRASEÑA
        // SOLICITUD DEL ENLACE
        // ========================================

        EMAIL_PASSWORD_RESET_HEADER_TITLE:
          'Recupera tu contraseña',

        EMAIL_PASSWORD_RESET_HEADER_SUBTITLE:
          'Te enviaremos un enlace para restablecerla.',

        EMAIL_PASSWORD_RESET_SEND_FALLBACK_EMAIL:
          'tu cuenta',

        EMAIL_PASSWORD_RESET_SEND_EMAIL_LABEL:
          'Correo electrónico',

        EMAIL_PASSWORD_RESET_SEND_EMAIL_PLACEHOLDER:
          'tu@correo.com',

        // Ambas variantes cubren las claves utilizadas
        // por los formularios de recuperación.
        EMAIL_PASSWORD_RESET_SEND_BTN:
          'Enviar enlace de recuperación',

        EMAIL_PASSWORD_RESET_SEND_SUBMIT_BTN:
          'Enviar enlace de recuperación',

        EMAIL_PASSWORD_RESET_SEND_SUCCESS:
          'Si existe una cuenta con ese correo, recibirás un enlace de recuperación.',

        EMAIL_PASSWORD_RESET_SEND_BEFORE_EMAIL:
          'Si hay una cuenta registrada con ',

        EMAIL_PASSWORD_RESET_SEND_AFTER_EMAIL:
          ', recibirás instrucciones para recuperar tu contraseña.',

        EMAIL_PASSWORD_RESET_SEND_BEFORE_RESEND:
          '¿No recibiste el correo? ',

        EMAIL_PASSWORD_RESET_SEND_RESEND_LINK:
          'Volver a enviar',

        EMAIL_PASSWORD_RESET_SEND_AFTER_RESEND:
          '',

        EMAIL_PASSWORD_RESET_SEND_SUCCESS_BACK_TO_SIGN_IN:
          'Volver al inicio de sesión',

        // ========================================
        // RESTABLECIMIENTO DE CONTRASEÑA
        // ========================================

        EMAIL_PASSWORD_RESET_SUBMIT_PW_HEADER_TITLE:
          'Nueva contraseña',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_HEADER_SUBTITLE:
          'Elige una nueva contraseña para tu cuenta.',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_NEW_PASSWORD_LABEL:
          'Nueva contraseña',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_NEW_PASSWORD_PLACEHOLDER:
          'Nueva contraseña',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_CONFIRM_PASSWORD_LABEL:
          'Confirmar contraseña',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_CONFIRM_PASSWORD_PLACEHOLDER:
          'Repite la contraseña',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_SUBMIT_BTN:
          'Guardar contraseña',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_CHANGE_PW_BTN:
          'Recuperar contraseña',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_INVALID_TOKEN_ERROR:
          'El enlace ha vencido o ya fue utilizado. Solicita uno nuevo.',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_PASSWORD_MISMATCH_ERROR:
          'Las contraseñas no coinciden.',

        // ========================================
        // CONTRASEÑA ACTUALIZADA
        // ========================================

        EMAIL_PASSWORD_RESET_SUBMIT_PW_SUCCESS_HEADER_TITLE:
          'Contraseña actualizada',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_SUCCESS_DESC:
          'Ya puedes iniciar sesión con tu nueva contraseña.',

        EMAIL_PASSWORD_RESET_SUBMIT_PW_SUCCESS_SIGN_IN_BTN:
          'Iniciar sesión',

        // ========================================
        // ERRORES GENERALES Y VALIDACIONES
        // ========================================

        SOMETHING_WENT_WRONG_ERROR:
          'No se pudo completar la solicitud. Inténtalo de nuevo.',

        SOMETHING_WENT_WRONG_ERROR_RELOAD:
          'No se pudo completar la solicitud. Recarga la página.',

        FIELD_IS_NOT_OPTIONAL_ERROR:
          'Completa este campo.',

        GENERAL_ERROR_EMAIL_NON_STRING:
          'Introduce un correo electrónico válido.',

        GENERAL_ERROR_EMAIL_INVALID:
          'Introduce un correo electrónico válido.',

        GENERAL_ERROR_PASSWORD_NON_STRING:
          'Introduce una contraseña válida.',

        // ========================================
        // PIE DE PÁGINA
        // ========================================

        BRANDING_POWERED_BY_START:
          'Tecnología de ',

        BRANDING_POWERED_BY_END:
          '',
      },
    },
  },

  recipeList: [
    EmailPassword.init(),

    Session.init({
      // Debe coincidir con el transporte configurado
      // en nuestro backend FastAPI.
      tokenTransferMethod: 'header',
    }),
  ],
});
