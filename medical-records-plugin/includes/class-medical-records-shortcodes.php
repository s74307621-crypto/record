<?php
if (!defined('ABSPATH')) {
    exit;
}

class Medical_Records_Shortcodes {
    
    public static function doctor_shortcode($atts) {
        $atts = shortcode_atts(array(), $atts);
        
        if (!current_user_can('edit_posts')) {
            return '<div class="mr-error">' . __('شما دسترسی مشاهده این صفحه را ندارید.', 'medical-records') . '</div>';
        }
        
        ob_start();
        include MR_PLUGIN_DIR . 'templates/frontend/doctor-view.php';
        return ob_get_clean();
    }
    
    public static function patient_shortcode($atts) {
        $atts = shortcode_atts(array(), $atts);
        
        if (!is_user_logged_in()) {
            return '<div class="mr-error">' . __('برای مشاهده این صفحه باید وارد شوید.', 'medical-records') . '</div>';
        }
        
        ob_start();
        include MR_PLUGIN_DIR . 'templates/frontend/patient-view.php';
        return ob_get_clean();
    }
}

add_shortcode('medical_records_doctor', array('Medical_Records_Shortcodes', 'doctor_shortcode'));
add_shortcode('medical_records_patient', array('Medical_Records_Shortcodes', 'patient_shortcode'));
