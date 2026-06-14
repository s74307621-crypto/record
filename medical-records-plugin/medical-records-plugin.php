<?php
/**
 * Plugin Name: Medical Records Management
 * Plugin URI: https://example.com/medical-records
 * Description: مدیریت پرونده‌های پزشکی با یکپارچگی بوکلی - نمایش پزشکان و بیماران از بوکلی، مدیریت پرونده‌ها، ویزیت‌ها و سوابق پزشکی
 * Version: 1.0.0
 * Author: Your Name
 * Author URI: https://example.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: medical-records
 * Domain Path: /languages
 */

if (!defined('ABSPATH')) {
    exit;
}

define('MR_PLUGIN_VERSION', '1.0.0');
define('MR_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('MR_PLUGIN_URL', plugin_dir_url(__FILE__));

class Medical_Records_Plugin {
    
    private static $instance = null;
    
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    private function __construct() {
        $this->init_hooks();
        $this->load_dependencies();
    }
    
    private function init_hooks() {
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
        
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_scripts'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_frontend_scripts'));
        
        add_shortcode('medical_records_doctor', array($this, 'doctor_shortcode'));
        add_shortcode('medical_records_patient', array($this, 'patient_shortcode'));
        
        add_action('wp_ajax_mr_create_medical_record', array($this, 'ajax_create_medical_record'));
        add_action('wp_ajax_mr_delete_medical_record', array($this, 'ajax_delete_medical_record'));
        add_action('wp_ajax_mr_get_medical_record', array($this, 'ajax_get_medical_record'));
        add_action('wp_ajax_mr_create_visit', array($this, 'ajax_create_visit'));
        add_action('wp_ajax_mr_get_visits', array($this, 'ajax_get_visits'));
        add_action('wp_ajax_mr_get_visit_details', array($this, 'ajax_get_visit_details'));
        add_action('wp_ajax_mr_save_medical_history', array($this, 'ajax_save_medical_history'));
        add_action('wp_ajax_mr_upload_file', array($this, 'ajax_upload_file'));
        
        add_action('wp_ajax_nopriv_mr_upload_file', array($this, 'ajax_upload_file'));
    }
    
    private function load_dependencies() {
        require_once MR_PLUGIN_DIR . 'includes/class-medical-records-db.php';
        require_once MR_PLUGIN_DIR . 'includes/class-medical-records-ajax.php';
        require_once MR_PLUGIN_DIR . 'includes/class-medical-records-shortcodes.php';
        require_once MR_PLUGIN_DIR . 'includes/class-medical-records-admin.php';
    }
    
    public function activate() {
        global $wpdb;
        $charset_collate = $wpdb->get_charset_collate();
        
        $sql_medical_records = "CREATE TABLE IF NOT EXISTS {$wpdb->prefix}mr_medical_records (
            id bigint(20) NOT NULL AUTO_INCREMENT,
            customer_id bigint(20) NOT NULL,
            doctor_id bigint(20) NOT NULL,
            blood_group varchar(10) DEFAULT '',
            special_diseases text DEFAULT '',
            age int(3) DEFAULT 0,
            current_medications text DEFAULT '',
            medical_files text DEFAULT '',
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY customer_id (customer_id),
            KEY doctor_id (doctor_id)
        ) $charset_collate;";
        
        $sql_visits = "CREATE TABLE IF NOT EXISTS {$wpdb->prefix}mr_visits (
            id bigint(20) NOT NULL AUTO_INCREMENT,
            medical_record_id bigint(20) NOT NULL,
            doctor_id bigint(20) NOT NULL,
            clinic_id bigint(20) NOT NULL,
            visit_date datetime DEFAULT CURRENT_TIMESTAMP,
            complaint text DEFAULT '',
            diagnosis text DEFAULT '',
            medications text DEFAULT '',
            files text DEFAULT '',
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY medical_record_id (medical_record_id),
            KEY doctor_id (doctor_id),
            KEY clinic_id (clinic_id)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql_medical_records);
        dbDelta($sql_visits);
        
        update_option('mr_plugin_version', MR_PLUGIN_VERSION);
    }
    
    public function deactivate() {
        // No data deletion on deactivation
    }
    
    public function add_admin_menu() {
        add_menu_page(
            __('مدیریت پرونده‌های پزشکی', 'medical-records'),
            __('پرونده‌های پزشکی', 'medical-records'),
            'manage_options',
            'medical-records',
            array($this, 'admin_page_callback'),
            'dashicons-heartbeat',
            30
        );
        
        add_submenu_page(
            'medical-records',
            __('لیست بیماران', 'medical-records'),
            __('لیست بیماران', 'medical-records'),
            'manage_options',
            'medical-records',
            array($this, 'admin_page_callback')
        );
    }
    
    public function admin_page_callback() {
        require_once MR_PLUGIN_DIR . 'templates/admin/patients-list.php';
    }
    
    public function enqueue_admin_scripts($hook) {
        if ($hook !== 'toplevel_page_medical-records') {
            return;
        }
        
        wp_enqueue_style('mr-admin-css', MR_PLUGIN_URL . 'assets/css/admin.css', array(), MR_PLUGIN_VERSION);
        wp_enqueue_script('jquery');
        wp_enqueue_script('select2', 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js', array('jquery'), '4.1.0', true);
        wp_enqueue_style('select2-css', 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css', array(), '4.1.0');
        wp_enqueue_script('persian-date', 'https://unpkg.com/persian-date@1.1.0/dist/persian-date.min.js', array(), '1.1.0', true);
        wp_enqueue_script('persian-datepicker', 'https://unpkg.com/persian-datepicker@1.2.0/dist/persian-datepicker.min.js', array('jquery', 'persian-date'), '1.2.0', true);
        wp_enqueue_style('persian-datepicker-css', 'https://unpkg.com/persian-datepicker@1.2.0/dist/css/persian-datepicker.min.css', array(), '1.2.0');
        wp_enqueue_script('mr-admin-js', MR_PLUGIN_URL . 'assets/js/admin.js', array('jquery', 'select2'), MR_PLUGIN_VERSION, true);
        
        wp_localize_script('mr-admin-js', 'mrAdminAjax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('mr_admin_nonce'),
            'strings' => array(
                'confirm_delete' => __('آیا از حذف این پرونده اطمینان دارید؟', 'medical-records'),
                'error' => __('خطایی رخ داده است.', 'medical-records'),
                'success' => __('عملیات با موفقیت انجام شد.', 'medical-records')
            )
        ));
    }
    
    public function enqueue_frontend_scripts() {
        wp_enqueue_style('mr-frontend-css', MR_PLUGIN_URL . 'assets/css/frontend.css', array(), MR_PLUGIN_VERSION);
        wp_enqueue_script('jquery');
        wp_enqueue_script('select2', 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js', array('jquery'), '4.1.0', true);
        wp_enqueue_style('select2-css', 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css', array(), '4.1.0');
        wp_enqueue_script('persian-date', 'https://unpkg.com/persian-date@1.1.0/dist/persian-date.min.js', array(), '1.1.0', true);
        wp_enqueue_script('persian-datepicker', 'https://unpkg.com/persian-datepicker@1.2.0/dist/persian-datepicker.min.js', array('jquery', 'persian-date'), '1.2.0', true);
        wp_enqueue_style('persian-datepicker-css', 'https://unpkg.com/persian-datepicker@1.2.0/dist/css/persian-datepicker.min.css', array(), '1.2.0');
        wp_enqueue_script('mr-frontend-js', MR_PLUGIN_URL . 'assets/js/frontend.js', array('jquery', 'select2'), MR_PLUGIN_VERSION, true);
        
        wp_localize_script('mr-frontend-js', 'mrFrontendAjax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('mr_frontend_nonce'),
            'strings' => array(
                'confirm_delete' => __('آیا از حذف این پرونده اطمینان دارید؟', 'medical-records'),
                'error' => __('خطایی رخ داده است.', 'medical-records'),
                'success' => __('عملیات با موفقیت انجام شد.', 'medical-records'),
                'upload_success' => __('فایل با موفقیت آپلود شد.', 'medical-records'),
                'upload_error' => __('خطا در آپلود فایل.', 'medical-records')
            )
        ));
    }
    
    public function doctor_shortcode($atts) {
        $atts = shortcode_atts(array(), $atts);
        ob_start();
        require_once MR_PLUGIN_DIR . 'templates/frontend/doctor-view.php';
        return ob_get_clean();
    }
    
    public function patient_shortcode($atts) {
        $atts = shortcode_atts(array(), $atts);
        ob_start();
        require_once MR_PLUGIN_DIR . 'templates/frontend/patient-view.php';
        return ob_get_clean();
    }
}

Medical_Records_Plugin::get_instance();
