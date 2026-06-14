<?php
if (!defined('ABSPATH')) {
    exit;
}

class Medical_Records_Shortcodes {
    
    public static function doctor_shortcode($atts) {
        $atts = shortcode_atts(array(), $atts);
        
        // Check if user is admin or has edit_posts capability OR is a Bookly staff member
        $can_access = current_user_can('edit_posts') || current_user_can('manage_options');
        
        if (!$can_access) {
            $current_user = wp_get_current_user();
            global $wpdb;
            $staff_table = $wpdb->prefix . 'bookly_staff';
            $is_staff = $wpdb->get_var($wpdb->prepare(
                "SELECT COUNT(*) FROM {$staff_table} WHERE wp_user_id = %d",
                $current_user->ID
            ));
            
            if ($is_staff > 0) {
                $can_access = true;
            }
        }
        
        if (!$can_access) {
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
